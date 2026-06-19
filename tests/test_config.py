"""Tests for environment-based runtime settings."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from utils.config import (
    DEFAULT_CLAUDE_MODEL,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_OPENAI_MODEL,
    get_settings,
    is_truthy,
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

    def test_truthy_environment_values(self) -> None:
        for value in ["1", "true", "TRUE", "yes", "on", " On "]:
            with self.subTest(value=value):
                self.assertTrue(is_truthy(value))

        for value in [None, "", "0", "false", "no", "off", "enabled"]:
            with self.subTest(value=value):
                self.assertFalse(is_truthy(value))


if __name__ == "__main__":
    unittest.main()
