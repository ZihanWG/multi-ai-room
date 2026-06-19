"""Tests for graceful behavior when provider API keys are missing."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from agents import ClaudeAgent, CriticAgent, GeminiAgent, ModeratorAgent, OpenAIAgent


class MissingApiKeyTests(unittest.TestCase):
    """Agents should fail clearly before making provider network calls."""

    @patch.dict("os.environ", {}, clear=True)
    def test_openai_agent_reports_missing_key(self) -> None:
        self.assertEqual(
            OpenAIAgent().run("测试问题"),
            "缺少 OPENAI_API_KEY，请在 .env 文件中配置。",
        )

    @patch.dict("os.environ", {}, clear=True)
    def test_claude_agent_reports_missing_key(self) -> None:
        self.assertEqual(
            ClaudeAgent().run("测试问题"),
            "缺少 ANTHROPIC_API_KEY，请在 .env 文件中配置。",
        )

    @patch.dict("os.environ", {}, clear=True)
    def test_gemini_agent_reports_missing_key(self) -> None:
        self.assertEqual(
            GeminiAgent().run("测试问题"),
            "缺少 GEMINI_API_KEY，请在 .env 文件中配置。",
        )

    @patch.dict("os.environ", {}, clear=True)
    def test_critic_agent_reports_missing_openai_key(self) -> None:
        self.assertEqual(
            CriticAgent().run(
                question="测试问题",
                gpt_answer="GPT 回答",
                claude_answer="Claude 回答",
                gemini_answer="Gemini 回答",
            ),
            "缺少 OPENAI_API_KEY，请在 .env 文件中配置。",
        )

    @patch.dict("os.environ", {}, clear=True)
    def test_moderator_agent_reports_missing_openai_key(self) -> None:
        self.assertEqual(
            ModeratorAgent().run(
                question="测试问题",
                gpt_answer="GPT 回答",
                claude_answer="Claude 回答",
                gemini_answer="Gemini 回答",
                critic_answer="Critic 回答",
            ),
            "缺少 OPENAI_API_KEY，请在 .env 文件中配置。",
        )


if __name__ == "__main__":
    unittest.main()
