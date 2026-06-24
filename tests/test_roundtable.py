"""Tests for visible cross-agent discussion prompts."""

from __future__ import annotations

import unittest

from utils.roundtable import build_peer_response_prompt, format_agent_blocks


class RoundtableTests(unittest.TestCase):
    """Validate peer-response prompt construction."""

    def test_build_peer_response_prompt_includes_peer_and_prior_outputs(self) -> None:
        prompt = build_peer_response_prompt(
            agent_name="Claude Agent",
            question="测试问题",
            own_output="Claude 首轮",
            peer_outputs={
                "GPT Agent": "GPT 首轮",
                "Gemini Agent": "Gemini 首轮",
            },
            prior_responses={"GPT Agent 交叉回应": "GPT 回应"},
        )

        self.assertIn("交叉回应任务", prompt)
        self.assertIn("用户原始问题：\n测试问题", prompt)
        self.assertIn("你的首轮观点：\nClaude 首轮", prompt)
        self.assertIn("### GPT Agent\nGPT 首轮", prompt)
        self.assertIn("### Gemini Agent\nGemini 首轮", prompt)
        self.assertIn("### GPT Agent 交叉回应\nGPT 回应", prompt)
        self.assertIn("不要输出隐藏思维链", prompt)

    def test_format_agent_blocks_can_truncate_outputs(self) -> None:
        blocks = format_agent_blocks(
            {"GPT Agent": "a" * 80},
            max_chars_per_agent=30,
        )

        self.assertIn("### GPT Agent", blocks)
        self.assertIn("已截断", blocks)
        self.assertLessEqual(len(blocks.split("\n", maxsplit=1)[1]), 30)

    def test_build_peer_response_prompt_truncates_context_blocks(self) -> None:
        prompt = build_peer_response_prompt(
            agent_name="GPT Agent",
            question="测试问题",
            own_output="o" * 80,
            peer_outputs={"Claude Agent": "c" * 80},
            max_chars_per_agent=30,
        )

        self.assertIn("已截断", prompt)
        self.assertNotIn("c" * 80, prompt)


if __name__ == "__main__":
    unittest.main()
