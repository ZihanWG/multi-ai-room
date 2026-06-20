"""Tests for multi-turn conversation helpers."""

from __future__ import annotations

import unittest

from utils.conversation import build_follow_up_prompt, coerce_outputs, truncate_text


class ConversationTests(unittest.TestCase):
    """Validate follow-up context construction."""

    def test_build_follow_up_prompt_contains_history_and_new_question(self) -> None:
        prompt = build_follow_up_prompt(
            "继续追问",
            [
                {
                    "question": "第一问",
                    "outputs": {
                        "GPT Agent": "GPT 输出",
                        "GPT Agent 交叉回应": "GPT 回应",
                        "Moderator Agent": "最终结论",
                    },
                }
            ],
        )

        self.assertIn("第一问", prompt)
        self.assertIn("GPT 输出", prompt)
        self.assertIn("GPT 回应", prompt)
        self.assertIn("最终结论", prompt)
        self.assertIn("继续追问", prompt)
        self.assertIn("同一谈话窗口", prompt)

    def test_build_follow_up_prompt_limits_history_turns(self) -> None:
        prompt = build_follow_up_prompt(
            "第三轮追问",
            [
                {"question": "第一问", "outputs": {"Moderator Agent": "第一轮"}},
                {"question": "第二问", "outputs": {"Moderator Agent": "第二轮"}},
            ],
            max_turns=1,
        )

        self.assertNotIn("第一问", prompt)
        self.assertIn("第二问", prompt)
        self.assertIn("第三轮追问", prompt)

    def test_coerce_outputs_handles_invalid_values(self) -> None:
        self.assertEqual(coerce_outputs(None), {})
        self.assertEqual(coerce_outputs({"Agent": 123}), {"Agent": "123"})

    def test_truncate_text_marks_truncated_content(self) -> None:
        self.assertEqual(truncate_text("short", 10), "short")
        self.assertIn("已截断", truncate_text("a" * 50, 20))


if __name__ == "__main__":
    unittest.main()
