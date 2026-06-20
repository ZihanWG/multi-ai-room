"""Tests for Markdown discussion export."""

from __future__ import annotations

import unittest

from utils.export import build_conversation_markdown, build_discussion_markdown


class ExportTests(unittest.TestCase):
    """Validate Markdown export behavior."""

    def test_build_discussion_markdown_uses_agent_order(self) -> None:
        markdown = build_discussion_markdown(
            "测试问题",
            {
                "Moderator Agent": "最终结论",
                "GPT Agent": "GPT 输出",
            },
        )

        self.assertIn("# 多 AI 讨论室结果 / Multi AI Discussion Result", markdown)
        self.assertIn("测试问题", markdown)
        self.assertLess(
            markdown.index("### GPT Agent"),
            markdown.index("### Moderator Agent"),
        )

    def test_build_discussion_markdown_includes_unknown_agents(self) -> None:
        markdown = build_discussion_markdown(
            "",
            {
                "Custom Agent": "",
            },
        )

        self.assertIn("_未记录原始问题 / Original question not recorded_", markdown)
        self.assertIn("### Custom Agent", markdown)
        self.assertIn("_无输出 / No output_", markdown)

    def test_build_conversation_markdown_exports_multiple_turns(self) -> None:
        markdown = build_conversation_markdown(
            [
                {
                    "question": "第一问",
                    "outputs": {"Moderator Agent": "第一轮结论"},
                },
                {
                    "question": "继续追问",
                    "outputs": {"GPT Agent": "第二轮 GPT 输出"},
                },
            ]
        )

        self.assertIn("第 1 轮 / Turn 1", markdown)
        self.assertIn("第一问", markdown)
        self.assertIn("第一轮结论", markdown)
        self.assertIn("第 2 轮 / Turn 2", markdown)
        self.assertIn("继续追问", markdown)

    def test_build_discussion_markdown_orders_cross_responses(self) -> None:
        markdown = build_discussion_markdown(
            "测试问题",
            {
                "Critic Agent": "评审",
                "GPT Agent 交叉回应": "GPT 回应",
                "Gemini Agent": "Gemini 首轮",
                "Claude Agent 交叉回应": "Claude 回应",
            },
        )

        self.assertLess(
            markdown.index("### Gemini Agent"),
            markdown.index("### GPT Agent 交叉回应"),
        )
        self.assertLess(
            markdown.index("### GPT Agent 交叉回应"),
            markdown.index("### Claude Agent 交叉回应"),
        )
        self.assertLess(
            markdown.index("### Claude Agent 交叉回应"),
            markdown.index("### Critic Agent"),
        )


if __name__ == "__main__":
    unittest.main()
