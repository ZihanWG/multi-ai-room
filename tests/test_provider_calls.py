"""Tests for review-stage provider selection helpers."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from agents.provider_calls import (
    available_providers,
    gemini_retry_attempts,
    missing_any_provider_message,
    provider_env_var,
    resolve_provider_sequence,
)
from utils.config import get_settings


class ProviderSelectionTests(unittest.TestCase):
    """Validate provider selection without making network calls."""

    @patch.dict(
        "os.environ",
        {
            "ANTHROPIC_API_KEY": "anthropic-key",
            "GEMINI_API_KEY": "gemini-key",
        },
        clear=True,
    )
    def test_available_providers_uses_auto_order(self) -> None:
        settings = get_settings()

        self.assertEqual(available_providers(settings), ("anthropic", "gemini"))
        self.assertEqual(
            resolve_provider_sequence(settings, "auto"),
            ("anthropic", "gemini"),
        )

    @patch.dict("os.environ", {"GEMINI_API_KEY": "gemini-key"}, clear=True)
    def test_explicit_provider_requires_matching_key(self) -> None:
        settings = get_settings()

        self.assertEqual(resolve_provider_sequence(settings, "gemini"), ("gemini",))
        self.assertEqual(resolve_provider_sequence(settings, "openai"), ())

    @patch.dict("os.environ", {"OPENAI_API_KEY": "openai-key"}, clear=True)
    def test_unknown_provider_falls_back_to_auto_sequence(self) -> None:
        settings = get_settings()

        self.assertEqual(resolve_provider_sequence(settings, "unknown"), ("openai",))

    def test_provider_env_var_and_missing_any_message(self) -> None:
        self.assertEqual(provider_env_var("anthropic"), "ANTHROPIC_API_KEY")
        self.assertIn("至少", missing_any_provider_message())

    def test_gemini_retry_attempts_include_initial_request(self) -> None:
        self.assertEqual(gemini_retry_attempts(0), 1)
        self.assertEqual(gemini_retry_attempts(2), 3)
        self.assertEqual(gemini_retry_attempts(-1), 1)


if __name__ == "__main__":
    unittest.main()
