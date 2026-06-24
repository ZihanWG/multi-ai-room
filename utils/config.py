"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


DEFAULT_OPENAI_MODEL = "gpt-5.5"
DEFAULT_CLAUDE_MODEL = "claude-opus-4-8"
DEFAULT_GEMINI_MODEL = "gemini-3.1-pro"
DEFAULT_REQUEST_TIMEOUT_SECONDS = 60.0
DEFAULT_PROVIDER_MAX_RETRIES = 2
DEFAULT_MAX_OUTPUT_TOKENS = 1200
DEFAULT_MAX_PROMPT_CONTEXT_CHARS = 1800
DEFAULT_CRITIC_PROVIDER = "auto"
DEFAULT_MODERATOR_PROVIDER = "auto"
SUPPORTED_REVIEW_PROVIDERS = {"auto", "openai", "anthropic", "gemini"}
TRUTHY_ENV_VALUES = {"1", "true", "yes", "on"}
PLACEHOLDER_API_KEY_VALUES = {
    "your_openai_api_key_here",
    "your_anthropic_api_key_here",
    "your_gemini_api_key_here",
    "placeholder",
    "changeme",
}


@dataclass(frozen=True)
class Settings:
    """Runtime settings for model providers."""

    openai_api_key: str | None
    anthropic_api_key: str | None
    gemini_api_key: str | None
    openai_model: str
    claude_model: str
    gemini_model: str
    demo_mode: bool
    request_timeout_seconds: float
    provider_max_retries: int
    max_output_tokens: int
    max_prompt_context_chars: int
    critic_provider: str
    moderator_provider: str


def is_truthy(value: str | None) -> bool:
    """Return whether an environment value should be treated as enabled."""

    return (value or "").strip().lower() in TRUTHY_ENV_VALUES


def normalize_api_key(value: str | None) -> str | None:
    """Return a cleaned API key, treating blanks and examples as missing."""

    cleaned = (value or "").strip()
    if not cleaned:
        return None

    lowered = cleaned.lower()
    if lowered in PLACEHOLDER_API_KEY_VALUES:
        return None
    if lowered.startswith("your_") and lowered.endswith("_here"):
        return None
    return cleaned


def read_text_env(name: str, default: str) -> str:
    """Read a non-empty string environment value."""

    value = os.getenv(name)
    if value is None:
        return default
    return value.strip() or default


def read_positive_int_env(name: str, default: int) -> int:
    """Read a positive integer environment value with a safe fallback."""

    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        parsed = int(raw_value.strip())
    except ValueError:
        return default

    return parsed if parsed > 0 else default


def read_non_negative_int_env(name: str, default: int) -> int:
    """Read a non-negative integer environment value with a safe fallback."""

    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        parsed = int(raw_value.strip())
    except ValueError:
        return default

    return parsed if parsed >= 0 else default


def read_positive_float_env(name: str, default: float) -> float:
    """Read a positive float environment value with a safe fallback."""

    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        parsed = float(raw_value.strip())
    except ValueError:
        return default

    return parsed if parsed > 0 else default


def read_provider_env(name: str, default: str) -> str:
    """Read a review-stage provider name with a safe fallback."""

    provider = read_text_env(name, default).lower()
    if provider not in SUPPORTED_REVIEW_PROVIDERS:
        return default
    return provider


def get_settings() -> Settings:
    """Read settings from environment variables.

    Missing API keys are intentionally allowed. Each Agent reports a clear
    provider-specific error so the Streamlit app can keep running.
    """

    return Settings(
        openai_api_key=normalize_api_key(os.getenv("OPENAI_API_KEY")),
        anthropic_api_key=normalize_api_key(os.getenv("ANTHROPIC_API_KEY")),
        gemini_api_key=normalize_api_key(os.getenv("GEMINI_API_KEY")),
        openai_model=read_text_env("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        claude_model=read_text_env("CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL),
        gemini_model=read_text_env("GEMINI_MODEL", DEFAULT_GEMINI_MODEL),
        demo_mode=is_truthy(os.getenv("DEMO_MODE")),
        request_timeout_seconds=read_positive_float_env(
            "REQUEST_TIMEOUT_SECONDS",
            DEFAULT_REQUEST_TIMEOUT_SECONDS,
        ),
        provider_max_retries=read_non_negative_int_env(
            "PROVIDER_MAX_RETRIES",
            DEFAULT_PROVIDER_MAX_RETRIES,
        ),
        max_output_tokens=read_positive_int_env(
            "MAX_OUTPUT_TOKENS",
            DEFAULT_MAX_OUTPUT_TOKENS,
        ),
        max_prompt_context_chars=read_positive_int_env(
            "MAX_PROMPT_CONTEXT_CHARS",
            DEFAULT_MAX_PROMPT_CONTEXT_CHARS,
        ),
        critic_provider=read_provider_env("CRITIC_PROVIDER", DEFAULT_CRITIC_PROVIDER),
        moderator_provider=read_provider_env(
            "MODERATOR_PROVIDER",
            DEFAULT_MODERATOR_PROVIDER,
        ),
    )
