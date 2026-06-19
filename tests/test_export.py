"""Tests for Markdown discussion export."""

from __future__ import annotations

import unittest

from utils.export import build_discussion_markdown


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


if __name__ == "__main__":
    unittest.main()
