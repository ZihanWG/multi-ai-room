"""Streamlit-free orchestration for a full multi-agent discussion."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Protocol

from agents import ClaudeAgent, CriticAgent, GeminiAgent, ModeratorAgent, OpenAIAgent
from utils.agent_errors import call_failed_message
from utils.discussion import (
    answer_for_review,
    build_review_context,
    get_cross_response_outputs,
    get_peer_outputs,
)
from utils.roundtable import build_peer_response_prompt

FIRST_ROUND_STAGE_KEYS = ("GPT Agent", "Claude Agent", "Gemini Agent")
CROSS_RESPONSE_STAGE_KEYS = (
    "GPT Agent 交叉回应",
    "Claude Agent 交叉回应",
    "Gemini Agent 交叉回应",
)
REVIEW_STAGE_KEYS = ("Critic Agent", "Moderator Agent")
DISCUSSION_STAGE_KEYS = (
    *FIRST_ROUND_STAGE_KEYS,
    *CROSS_RESPONSE_STAGE_KEYS,
    *REVIEW_STAGE_KEYS,
)


class QuestionAgent(Protocol):
    """Agent interface for first-round and peer-response calls."""

    def run(self, question: str) -> str:
        """Run the agent for a plain prompt."""
        ...


class CriticAgentRunner(Protocol):
    """Agent interface for the critic stage."""

    def run(
        self,
        question: str,
        gpt_answer: str,
        claude_answer: str,
        gemini_answer: str,
        peer_discussion: str = "",
    ) -> str:
        """Run the critic stage."""
        ...


class ModeratorAgentRunner(Protocol):
    """Agent interface for the moderator stage."""

    def run(
        self,
        question: str,
        gpt_answer: str,
        claude_answer: str,
        gemini_answer: str,
        critic_answer: str,
        peer_discussion: str = "",
    ) -> str:
        """Run the moderator stage."""
        ...


@dataclass(frozen=True)
class DiscussionEvent:
    """Progress event emitted by the discussion runner."""

    kind: str
    outputs: Mapping[str, str] = field(default_factory=dict)
    active_keys: frozenset[str] = frozenset()
    completed_keys: tuple[str, ...] = ()


DiscussionEventHandler = Callable[[DiscussionEvent], None]
AgentRunner = Callable[[], str]


def emit_event(
    on_event: DiscussionEventHandler | None,
    *,
    kind: str,
    outputs: Mapping[str, str],
    active_keys: set[str] | None = None,
    completed_keys: tuple[str, ...] = (),
) -> None:
    """Emit an immutable snapshot of discussion progress."""

    if on_event is None:
        return

    on_event(
        DiscussionEvent(
            kind=kind,
            outputs=dict(outputs),
            active_keys=frozenset(active_keys or set()),
            completed_keys=completed_keys,
        )
    )


def run_safely(stage_key: str, runner: AgentRunner) -> str:
    """Run one stage and convert unexpected exceptions into failure output."""

    try:
        return runner()
    except Exception as exc:
        return call_failed_message(stage_key, exc)


def future_result_safely(stage_key: str, future: Future[str]) -> str:
    """Resolve a future and convert worker exceptions into failure output."""

    try:
        return future.result()
    except Exception as exc:
        return call_failed_message(stage_key, exc)


def run_first_round(
    runners: Mapping[str, AgentRunner],
    outputs: dict[str, str],
    *,
    on_event: DiscussionEventHandler | None,
) -> None:
    """Run independent first-round agents concurrently."""

    stage_keys = tuple(runners)
    emit_event(
        on_event,
        kind="active",
        outputs=outputs,
        active_keys=set(stage_keys),
    )

    with ThreadPoolExecutor(max_workers=len(runners)) as executor:
        futures = {key: executor.submit(runner) for key, runner in runners.items()}
        for key, future in futures.items():
            outputs[key] = future_result_safely(key, future)

    emit_event(
        on_event,
        kind="completed",
        outputs=outputs,
        completed_keys=stage_keys,
    )


def run_stage(
    stage_key: str,
    runner: AgentRunner,
    outputs: dict[str, str],
    *,
    on_event: DiscussionEventHandler | None,
) -> None:
    """Run one dependent stage and emit progress events."""

    emit_event(
        on_event,
        kind="active",
        outputs=outputs,
        active_keys={stage_key},
    )
    outputs[stage_key] = run_safely(stage_key, runner)
    emit_event(
        on_event,
        kind="completed",
        outputs=outputs,
        completed_keys=(stage_key,),
    )


def run_discussion_flow(
    question: str,
    *,
    max_context_chars: int,
    on_event: DiscussionEventHandler | None = None,
    gpt_agent: QuestionAgent | None = None,
    claude_agent: QuestionAgent | None = None,
    gemini_agent: QuestionAgent | None = None,
    critic_agent_factory: Callable[[], CriticAgentRunner] = CriticAgent,
    moderator_agent_factory: Callable[[], ModeratorAgentRunner] = ModeratorAgent,
) -> dict[str, str]:
    """Run the full discussion flow and return outputs by stage key."""

    outputs: dict[str, str] = {}
    gpt_runner = gpt_agent or OpenAIAgent()
    claude_runner = claude_agent or ClaudeAgent()
    gemini_runner = gemini_agent or GeminiAgent()

    run_first_round(
        {
            "GPT Agent": lambda: gpt_runner.run(question),
            "Claude Agent": lambda: claude_runner.run(question),
            "Gemini Agent": lambda: gemini_runner.run(question),
        },
        outputs,
        on_event=on_event,
    )
    run_stage(
        "GPT Agent 交叉回应",
        lambda: gpt_runner.run(
            build_peer_response_prompt(
                agent_name="GPT Agent",
                question=question,
                own_output=outputs["GPT Agent"],
                peer_outputs=get_peer_outputs(outputs, current_agent_key="GPT Agent"),
                max_chars_per_agent=max_context_chars,
            )
        ),
        outputs,
        on_event=on_event,
    )
    run_stage(
        "Claude Agent 交叉回应",
        lambda: claude_runner.run(
            build_peer_response_prompt(
                agent_name="Claude Agent",
                question=question,
                own_output=outputs["Claude Agent"],
                peer_outputs=get_peer_outputs(
                    outputs,
                    current_agent_key="Claude Agent",
                ),
                prior_responses=get_cross_response_outputs(outputs),
                max_chars_per_agent=max_context_chars,
            )
        ),
        outputs,
        on_event=on_event,
    )
    run_stage(
        "Gemini Agent 交叉回应",
        lambda: gemini_runner.run(
            build_peer_response_prompt(
                agent_name="Gemini Agent",
                question=question,
                own_output=outputs["Gemini Agent"],
                peer_outputs=get_peer_outputs(
                    outputs,
                    current_agent_key="Gemini Agent",
                ),
                prior_responses=get_cross_response_outputs(outputs),
                max_chars_per_agent=max_context_chars,
            )
        ),
        outputs,
        on_event=on_event,
    )
    run_stage(
        "Critic Agent",
        lambda: critic_agent_factory().run(
            question=question,
            gpt_answer=answer_for_review(
                outputs,
                "GPT Agent",
                max_chars=max_context_chars,
            ),
            claude_answer=answer_for_review(
                outputs,
                "Claude Agent",
                max_chars=max_context_chars,
            ),
            gemini_answer=answer_for_review(
                outputs,
                "Gemini Agent",
                max_chars=max_context_chars,
            ),
            peer_discussion=build_review_context(
                outputs,
                max_chars_per_agent=max_context_chars,
            ),
        ),
        outputs,
        on_event=on_event,
    )
    run_stage(
        "Moderator Agent",
        lambda: moderator_agent_factory().run(
            question=question,
            gpt_answer=answer_for_review(
                outputs,
                "GPT Agent",
                max_chars=max_context_chars,
            ),
            claude_answer=answer_for_review(
                outputs,
                "Claude Agent",
                max_chars=max_context_chars,
            ),
            gemini_answer=answer_for_review(
                outputs,
                "Gemini Agent",
                max_chars=max_context_chars,
            ),
            critic_answer=answer_for_review(
                outputs,
                "Critic Agent",
                max_chars=max_context_chars,
            ),
            peer_discussion=build_review_context(
                outputs,
                max_chars_per_agent=max_context_chars,
            ),
        ),
        outputs,
        on_event=on_event,
    )

    return outputs
