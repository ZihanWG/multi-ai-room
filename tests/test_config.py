"""Tests for environment-based runtime settings."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from utils.config import (
    DEFAULT_CLAUDE_MODEL,
    DEFAULT_CRITIC_PROVIDER,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_MAX_ATTACHMENT_CONTEXT_CHARS,
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_MAX_PROMPT_CONTEXT_CHARS,
    DEFAULT_MODERATOR_PROVIDER,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_PROVIDER_MAX_RETRIES,
    DEFAULT_REQUEST_TIMEOUT_SECONDS,
    get_settings,
    is_truthy,
    normalize_api_key,
)


class SettingsTests(unittest.TestCase):
    """Validate settings behavior without requiring real API keys."""

    @patch.dict("os.environ", {}, clear=True)
    def test_defaults_when_environment_is_empty(self) -> None:
        settings = get_settings()

        self.assertIsNone(settings.openai_api_key)
        self.assertIsNone(settings.anthropic_api_key)
        self.assertIsNone(settings.gemini_api_key)
        self.assertEqual(settings.openai_model, DEFAULT_OPENAI_MODEL)
        self.assertEqual(settings.claude_model, DEFAULT_CLAUDE_MODEL)
        self.assertEqual(settings.gemini_model, DEFAULT_GEMINI_MODEL)
        self.assertFalse(settings.demo_mode)
        self.assertEqual(
            settings.request_timeout_seconds,
            DEFAULT_REQUEST_TIMEOUT_SECONDS,
        )
        self.assertEqual(settings.provider_max_retries, DEFAULT_PROVIDER_MAX_RETRIES)
        self.assertEqual(settings.max_output_tokens, DEFAULT_MAX_OUTPUT_TOKENS)
        self.assertEqual(
            settings.max_prompt_context_chars,
            DEFAULT_MAX_PROMPT_CONTEXT_CHARS,
        )
        self.assertEqual(
            settings.max_attachment_context_chars,
            DEFAULT_MAX_ATTACHMENT_CONTEXT_CHARS,
        )
        self.assertEqual(settings.critic_provider, DEFAULT_CRITIC_PROVIDER)
        self.assertEqual(settings.moderator_provider, DEFAULT_MODERATOR_PROVIDER)

    @patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": "openai-test-key",
            "ANTHROPIC_API_KEY": "anthropic-test-key",
            "GEMINI_API_KEY": "gemini-test-key",
            "OPENAI_MODEL": "openai-test-model",
            "CLAUDE_MODEL": "claude-test-model",
            "GEMINI_MODEL": "gemini-test-model",
            "DEMO_MODE": "true",
            "REQUEST_TIMEOUT_SECONDS": "12.5",
            "PROVIDER_MAX_RETRIES": "0",
            "MAX_OUTPUT_TOKENS": "900",
            "MAX_PROMPT_CONTEXT_CHARS": "1400",
            "MAX_ATTACHMENT_CONTEXT_CHARS": "700",
            "CRITIC_PROVIDER": "anthropic",
            "MODERATOR_PROVIDER": "gemini",
        },
        clear=True,
    )
    def test_environment_values_override_defaults(self) -> None:
        settings = get_settings()

        self.assertEqual(settings.openai_api_key, "openai-test-key")
        self.assertEqual(settings.anthropic_api_key, "anthropic-test-key")
        self.assertEqual(settings.gemini_api_key, "gemini-test-key")
        self.assertEqual(settings.openai_model, "openai-test-model")
        self.assertEqual(settings.claude_model, "claude-test-model")
        self.assertEqual(settings.gemini_model, "gemini-test-model")
        self.assertTrue(settings.demo_mode)
        self.assertEqual(settings.request_timeout_seconds, 12.5)
        self.assertEqual(settings.provider_max_retries, 0)
        self.assertEqual(settings.max_output_tokens, 900)
        self.assertEqual(settings.max_prompt_context_chars, 1400)
        self.assertEqual(settings.max_attachment_context_chars, 700)
        self.assertEqual(settings.critic_provider, "anthropic")
        self.assertEqual(settings.moderator_provider, "gemini")

    @patch.dict(
        "os.environ",
        {
            "OPENAI_API_KEY": " your_openai_api_key_here ",
            "ANTHROPIC_API_KEY": "",
            "GEMINI_API_KEY": "your_gemini_api_key_here",
            "REQUEST_TIMEOUT_SECONDS": "-1",
            "PROVIDER_MAX_RETRIES": "-1",
            "MAX_OUTPUT_TOKENS": "not-a-number",
            "MAX_PROMPT_CONTEXT_CHARS": "0",
            "MAX_ATTACHMENT_CONTEXT_CHARS": "bad",
            "CRITIC_PROVIDER": "not-real",
            "MODERATOR_PROVIDER": "not-real",
        },
        clear=True,
    )
    def test_placeholders_and_invalid_numbers_fall_back(self) -> None:
        settings = get_settings()

        self.assertIsNone(settings.openai_api_key)
        self.assertIsNone(settings.anthropic_api_key)
        self.assertIsNone(settings.gemini_api_key)
        self.assertEqual(
            settings.request_timeout_seconds,
            DEFAULT_REQUEST_TIMEOUT_SECONDS,
        )
        self.assertEqual(settings.provider_max_retries, DEFAULT_PROVIDER_MAX_RETRIES)
        self.assertEqual(settings.max_output_tokens, DEFAULT_MAX_OUTPUT_TOKENS)
        self.assertEqual(
            settings.max_prompt_context_chars,
            DEFAULT_MAX_PROMPT_CONTEXT_CHARS,
        )
        self.assertEqual(
            settings.max_attachment_context_chars,
            DEFAULT_MAX_ATTACHMENT_CONTEXT_CHARS,
        )
        self.assertEqual(settings.critic_provider, DEFAULT_CRITIC_PROVIDER)
        self.assertEqual(settings.moderator_provider, DEFAULT_MODERATOR_PROVIDER)

    def test_normalize_api_key_trims_real_values(self) -> None:
        self.assertEqual(normalize_api_key(" real-key "), "real-key")
        self.assertIsNone(normalize_api_key("your_provider_key_here"))

    def test_truthy_environment_values(self) -> None:
        for value in ["1", "true", "TRUE", "yes", "on", " On "]:
            with self.subTest(value=value):
                self.assertTrue(is_truthy(value))

        falsy_values: list[str | None] = [
            None,
            "",
            "0",
            "false",
            "no",
            "off",
            "enabled",
        ]
        for falsy in falsy_values:
            with self.subTest(value=falsy):
                self.assertFalse(is_truthy(falsy))


if __name__ == "__main__":
    unittest.main()
