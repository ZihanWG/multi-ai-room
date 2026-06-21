"""Tests for cross-agent discussion context helpers."""

from __future__ import annotations

import unittest

from utils.agent_errors import missing_key_message
from utils.discussion import (
    answer_for_review,
    build_review_context,
    get_cross_response_outputs,
    get_peer_outputs,
)


class DiscussionContextTests(unittest.TestCase):
    """Validate the context fed into later discussion stages."""

    def test_get_peer_outputs_excludes_current_agent(self) -> None:
        outputs = {"GPT Agent": "g", "Claude Agent": "c", "Gemini Agent": "m"}
        peers = get_peer_outputs(outputs, current_agent_key="GPT Agent")
        self.assertEqual(peers, {"Claude Agent": "c", "Gemini Agent": "m"})

    def test_get_peer_outputs_skips_failures(self) -> None:
        outputs = {
            "GPT Agent": "g",
            "Claude Agent": missing_key_message("ANTHROPIC_API_KEY"),
            "Gemini Agent": "m",
        }
        peers = get_peer_outputs(outputs, current_agent_key="GPT Agent")
        self.assertEqual(peers, {"Gemini Agent": "m"})

    def test_get_cross_response_outputs_orders_and_skips_failures(self) -> None:
        outputs = {
            "Gemini Agent 交叉回应": "gm",
            "GPT Agent 交叉回应": "gp",
            "Claude Agent 交叉回应": missing_key_message("ANTHROPIC_API_KEY"),
        }
        responses = get_cross_response_outputs(outputs)
        self.assertEqual(
            list(responses), ["GPT Agent 交叉回应", "Gemini Agent 交叉回应"]
        )

    def test_build_review_context_empty_when_no_responses(self) -> None:
        self.assertEqual(build_review_context({"GPT Agent": "g"}), "")

    def test_build_review_context_includes_responses(self) -> None:
        context = build_review_context({"GPT Agent 交叉回应": "回应内容"})
        self.assertIn("交叉回应记录", context)
        self.assertIn("### GPT Agent 交叉回应", context)
        self.assertIn("回应内容", context)

    def test_answer_for_review_passthrough(self) -> None:
        self.assertEqual(
            answer_for_review({"GPT Agent": "真实分析"}, "GPT Agent"), "真实分析"
        )

    def test_answer_for_review_masks_failure(self) -> None:
        outputs = {"Claude Agent": missing_key_message("ANTHROPIC_API_KEY")}
        masked = answer_for_review(outputs, "Claude Agent")
        self.assertIn("未能产出有效回答", masked)
        self.assertNotIn("ANTHROPIC_API_KEY", masked)


if __name__ == "__main__":
    unittest.main()
