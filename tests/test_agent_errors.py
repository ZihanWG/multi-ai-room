"""Tests for shared agent failure messages and detection."""

from __future__ import annotations

import unittest

from utils.agent_errors import (
    call_failed_message,
    is_failure_output,
    missing_key_message,
)


class AgentErrorTests(unittest.TestCase):
    """Validate failure message formatting and detection."""

    def test_missing_key_message_format(self) -> None:
        self.assertEqual(
            missing_key_message("OPENAI_API_KEY"),
            "缺少 OPENAI_API_KEY，请在 .env 文件中配置。",
        )

    def test_call_failed_message_format(self) -> None:
        self.assertEqual(
            call_failed_message("GPT Agent", "boom"),
            "GPT Agent 调用失败：boom",
        )

    def test_is_failure_output_detects_missing_key(self) -> None:
        self.assertTrue(is_failure_output(missing_key_message("GEMINI_API_KEY")))

    def test_is_failure_output_detects_call_failure(self) -> None:
        self.assertTrue(
            is_failure_output(call_failed_message("Claude Agent", ValueError("x")))
        )

    def test_is_failure_output_false_for_normal_text(self) -> None:
        self.assertFalse(is_failure_output("这是一段正常的分析内容。"))


if __name__ == "__main__":
    unittest.main()
