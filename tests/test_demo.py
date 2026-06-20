"""Tests for deterministic demo responses."""

from __future__ import annotations

import unittest

from utils.demo import build_demo_response, extract_display_question


class DemoTests(unittest.TestCase):
    """Validate demo-mode formatting."""

    def test_extract_display_question_from_follow_up_prompt(self) -> None:
        prompt = """
历史讨论：

...

用户新的追问：
继续追问内容

请继续按当前 Agent 角色完成本轮回答。
""".strip()

        self.assertEqual(extract_display_question(prompt), "继续追问内容")

    def test_demo_response_uses_extracted_follow_up_question(self) -> None:
        response = build_demo_response(
            "GPT Agent",
            "用户新的追问：\n继续追问内容\n\n请继续按当前 Agent 角色完成本轮回答。",
        )

        self.assertIn("继续追问内容", response)
        self.assertNotIn("请继续按当前 Agent 角色完成本轮回答", response)

    def test_extract_display_question_from_peer_response_prompt(self) -> None:
        prompt = """
交叉回应任务

用户原始问题：
原始问题内容

你当前身份：
GPT Agent
""".strip()

        self.assertEqual(extract_display_question(prompt), "原始问题内容")

    def test_demo_peer_response_uses_roundtable_format(self) -> None:
        response = build_demo_response(
            "Gemini Agent",
            """
交叉回应任务

用户原始问题：
原始问题内容

你当前身份：
Gemini Agent
""".strip(),
        )

        self.assertIn("交叉回应", response)
        self.assertIn("回应 GPT", response)
        self.assertIn("原始问题内容", response)


if __name__ == "__main__":
    unittest.main()
