"""Tests for review-stage provider selection helpers."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from agents.provider_calls import (
    available_providers,
    build_anthropic_user_content,
    build_gemini_contents,
    build_openai_user_content,
    gemini_retry_attempts,
    missing_any_provider_message,
    provider_env_var,
    resolve_provider_sequence,
)
from utils.attachments import PreparedAttachment
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

    def test_multimodal_content_builders_include_image_parts(self) -> None:
        attachment = PreparedAttachment(
            name="diagram.png",
            mime_type="image/png",
            size_bytes=3,
            content=b"\x89PNG\r\n\x1a\nabc",
            kind="image",
        )

        openai_content = build_openai_user_content("question", [attachment])
        anthropic_content = build_anthropic_user_content("question", [attachment])
        gemini_contents = build_gemini_contents("question", [attachment])

        self.assertIsInstance(openai_content, list)
        self.assertEqual(openai_content[1]["type"], "input_image")
        self.assertIsInstance(anthropic_content, list)
        self.assertEqual(anthropic_content[1]["type"], "image")
        self.assertIsInstance(gemini_contents, list)
        self.assertEqual(gemini_contents[0].parts[0].text, "question")


if __name__ == "__main__":
    unittest.main()
