"""Tests for the Streamlit-free discussion runner."""

from __future__ import annotations

import unittest
from collections.abc import Sequence

from utils.agent_errors import CALL_FAILED_MARKER
from utils.attachments import PreparedAttachment
from utils.discussion_runner import (
    DISCUSSION_STAGE_KEYS,
    DiscussionEvent,
    run_discussion_flow,
)


class SequenceQuestionAgent:
    """Fake first-round agent that returns a configured sequence."""

    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.prompts: list[str] = []

    def run(
        self,
        question: str,
        attachments: Sequence[PreparedAttachment] | None = None,
    ) -> str:
        self.prompts.append(question)
        index = len(self.prompts) - 1
        if index >= len(self.responses):
            return self.responses[-1]
        return self.responses[index]


class ExplodingQuestionAgent:
    """Fake agent that always fails."""

    def run(
        self,
        question: str,
        attachments: Sequence[PreparedAttachment] | None = None,
    ) -> str:
        raise RuntimeError("agent exploded")


class RecordingAttachmentQuestionAgent:
    """Fake agent that records attachment kwargs."""

    def __init__(self, response: str) -> None:
        self.response = response
        self.attachments_seen: list[object] = []

    def run(
        self,
        question: str,
        attachments: Sequence[PreparedAttachment] | None = None,
    ) -> str:
        self.attachments_seen.append(attachments)
        return self.response


class RecordingCriticAgent:
    """Fake critic that records inputs."""

    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def run(
        self,
        question: str,
        gpt_answer: str,
        claude_answer: str,
        gemini_answer: str,
        peer_discussion: str = "",
    ) -> str:
        self.calls.append(
            {
                "question": question,
                "gpt_answer": gpt_answer,
                "claude_answer": claude_answer,
                "gemini_answer": gemini_answer,
                "peer_discussion": peer_discussion,
            }
        )
        return "critic output"


class RecordingModeratorAgent:
    """Fake moderator that records inputs."""

    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def run(
        self,
        question: str,
        gpt_answer: str,
        claude_answer: str,
        gemini_answer: str,
        critic_answer: str,
        peer_discussion: str = "",
    ) -> str:
        self.calls.append(
            {
                "question": question,
                "gpt_answer": gpt_answer,
                "claude_answer": claude_answer,
                "gemini_answer": gemini_answer,
                "critic_answer": critic_answer,
                "peer_discussion": peer_discussion,
            }
        )
        return "moderator output"


class DiscussionRunnerTests(unittest.TestCase):
    """Validate the pure discussion flow."""

    def test_run_discussion_flow_returns_all_stages_and_events(self) -> None:
        events: list[DiscussionEvent] = []
        critic = RecordingCriticAgent()
        moderator = RecordingModeratorAgent()

        outputs = run_discussion_flow(
            "测试问题",
            max_context_chars=80,
            on_event=events.append,
            gpt_agent=SequenceQuestionAgent(["gpt first", "gpt cross"]),
            claude_agent=SequenceQuestionAgent(["claude first", "claude cross"]),
            gemini_agent=SequenceQuestionAgent(["gemini first", "gemini cross"]),
            critic_agent_factory=lambda: critic,
            moderator_agent_factory=lambda: moderator,
        )

        self.assertEqual(tuple(outputs), DISCUSSION_STAGE_KEYS)
        self.assertEqual(outputs["Critic Agent"], "critic output")
        self.assertEqual(outputs["Moderator Agent"], "moderator output")
        self.assertEqual(events[0].kind, "active")
        self.assertEqual(
            events[0].active_keys,
            frozenset({"GPT Agent", "Claude Agent", "Gemini Agent"}),
        )
        self.assertEqual(
            events[1].completed_keys,
            ("GPT Agent", "Claude Agent", "Gemini Agent"),
        )
        self.assertEqual(events[-1].completed_keys, ("Moderator Agent",))
        self.assertEqual(critic.calls[0]["question"], "测试问题")
        self.assertEqual(moderator.calls[0]["critic_answer"], "critic output")

    def test_run_discussion_flow_converts_agent_exceptions(self) -> None:
        critic = RecordingCriticAgent()

        outputs = run_discussion_flow(
            "测试问题",
            max_context_chars=80,
            gpt_agent=ExplodingQuestionAgent(),
            claude_agent=SequenceQuestionAgent(["claude first", "claude cross"]),
            gemini_agent=SequenceQuestionAgent(["gemini first", "gemini cross"]),
            critic_agent_factory=lambda: critic,
            moderator_agent_factory=RecordingModeratorAgent,
        )

        self.assertIn(CALL_FAILED_MARKER, outputs["GPT Agent"])
        self.assertIn(CALL_FAILED_MARKER, outputs["GPT Agent 交叉回应"])
        self.assertIn("未能产出有效回答", critic.calls[0]["gpt_answer"])
        self.assertIn("Moderator Agent", outputs)

    def test_run_discussion_flow_limits_context_passed_to_later_stages(self) -> None:
        gpt = SequenceQuestionAgent(["g" * 80, "gpt cross"])
        claude = SequenceQuestionAgent(["c" * 80, "claude cross"])
        gemini = SequenceQuestionAgent(["m" * 80, "gemini cross"])
        critic = RecordingCriticAgent()

        run_discussion_flow(
            "测试问题",
            max_context_chars=30,
            gpt_agent=gpt,
            claude_agent=claude,
            gemini_agent=gemini,
            critic_agent_factory=lambda: critic,
            moderator_agent_factory=RecordingModeratorAgent,
        )

        self.assertIn("已截断", gpt.prompts[1])
        self.assertNotIn("c" * 80, gpt.prompts[1])
        self.assertIn("已截断", critic.calls[0]["gpt_answer"])
        self.assertLessEqual(len(critic.calls[0]["gpt_answer"]), 30)

    def test_run_discussion_flow_passes_attachments_to_first_round(self) -> None:
        attachment = PreparedAttachment(
            name="diagram.png",
            mime_type="image/png",
            size_bytes=3,
            content=b"abc",
            kind="image",
        )
        gpt = RecordingAttachmentQuestionAgent("gpt output")
        claude = RecordingAttachmentQuestionAgent("claude output")
        gemini = RecordingAttachmentQuestionAgent("gemini output")

        run_discussion_flow(
            "测试问题",
            max_context_chars=80,
            attachments=[attachment],
            gpt_agent=gpt,
            claude_agent=claude,
            gemini_agent=gemini,
            critic_agent_factory=RecordingCriticAgent,
            moderator_agent_factory=RecordingModeratorAgent,
        )

        self.assertEqual(gpt.attachments_seen[0], [attachment])
        self.assertEqual(claude.attachments_seen[0], [attachment])
        self.assertEqual(gemini.attachments_seen[0], [attachment])
        self.assertIsNone(gpt.attachments_seen[1])


if __name__ == "__main__":
    unittest.main()
