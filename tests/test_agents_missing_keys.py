"""Tests for graceful behavior when provider API keys are missing."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from agents import ClaudeAgent, CriticAgent, GeminiAgent, ModeratorAgent, OpenAIAgent
from agents.provider_calls import missing_any_provider_message


class MissingApiKeyTests(unittest.TestCase):
    """Agents should fail clearly before making provider network calls."""

    @patch.dict("os.environ", {}, clear=True)
    def test_openai_agent_reports_missing_key(self) -> None:
        self.assertEqual(
            OpenAIAgent().run("测试问题"),
            "缺少 OPENAI_API_KEY，请在 .env 文件中配置。",
        )

    @patch.dict("os.environ", {"DEMO_MODE": "true"}, clear=True)
    def test_demo_mode_returns_local_outputs_without_keys(self) -> None:
        self.assertIn("Demo 模式提示", OpenAIAgent().run("测试问题"))
        self.assertIn("Demo 模式提示", ClaudeAgent().run("测试问题"))
        self.assertIn("Demo 模式提示", GeminiAgent().run("测试问题"))
        self.assertIn(
            "Demo 模式提示",
            CriticAgent().run(
                question="测试问题",
                gpt_answer="GPT 回答",
                claude_answer="Claude 回答",
                gemini_answer="Gemini 回答",
            ),
        )
        self.assertIn(
            "Demo 模式提示",
            ModeratorAgent().run(
                question="测试问题",
                gpt_answer="GPT 回答",
                claude_answer="Claude 回答",
                gemini_answer="Gemini 回答",
                critic_answer="Critic 回答",
            ),
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
    def test_critic_agent_reports_missing_review_provider(self) -> None:
        self.assertEqual(
            CriticAgent().run(
                question="测试问题",
                gpt_answer="GPT 回答",
                claude_answer="Claude 回答",
                gemini_answer="Gemini 回答",
            ),
            missing_any_provider_message(),
        )

    @patch.dict("os.environ", {}, clear=True)
    def test_moderator_agent_reports_missing_review_provider(self) -> None:
        self.assertEqual(
            ModeratorAgent().run(
                question="测试问题",
                gpt_answer="GPT 回答",
                claude_answer="Claude 回答",
                gemini_answer="Gemini 回答",
                critic_answer="Critic 回答",
            ),
            missing_any_provider_message(),
        )

    @patch.dict("os.environ", {"CRITIC_PROVIDER": "gemini"}, clear=True)
    def test_explicit_critic_provider_reports_matching_missing_key(self) -> None:
        self.assertEqual(
            CriticAgent().run(
                question="测试问题",
                gpt_answer="GPT 回答",
                claude_answer="Claude 回答",
                gemini_answer="Gemini 回答",
            ),
            "缺少 GEMINI_API_KEY，请在 .env 文件中配置。",
        )

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "anthropic-key"}, clear=True)
    def test_critic_auto_uses_available_non_openai_provider(self) -> None:
        with patch(
            "agents.critic_agent.generate_with_provider",
            return_value="Critic via Claude",
        ) as generate:
            output = CriticAgent().run(
                question="测试问题",
                gpt_answer="GPT 回答",
                claude_answer="Claude 回答",
                gemini_answer="Gemini 回答",
            )

        self.assertEqual(output, "Critic via Claude")
        self.assertEqual(generate.call_args.kwargs["provider"], "anthropic")

    @patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": "openai-key",
            "ANTHROPIC_API_KEY": "anthropic-key",
        },
        clear=True,
    )
    def test_moderator_auto_falls_back_after_provider_failure(self) -> None:
        def generate_side_effect(**kwargs: object) -> str:
            if kwargs["provider"] == "openai":
                raise RuntimeError("openai unavailable")
            return "Moderator via Claude"

        with patch(
            "agents.moderator_agent.generate_with_provider",
            side_effect=generate_side_effect,
        ) as generate:
            output = ModeratorAgent().run(
                question="测试问题",
                gpt_answer="GPT 回答",
                claude_answer="Claude 回答",
                gemini_answer="Gemini 回答",
                critic_answer="Critic 回答",
            )

        self.assertEqual(output, "Moderator via Claude")
        self.assertEqual(
            [call.kwargs["provider"] for call in generate.call_args_list],
            ["openai", "anthropic"],
        )


if __name__ == "__main__":
    unittest.main()
