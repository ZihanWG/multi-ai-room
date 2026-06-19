"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


DEFAULT_OPENAI_MODEL = "gpt-4.1"
DEFAULT_CLAUDE_MODEL = "claude-3-5-sonnet-latest"
DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"
TRUTHY_ENV_VALUES = {"1", "true", "yes", "on"}


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


def is_truthy(value: str | None) -> bool:
    """Return whether an environment value should be treated as enabled."""

    return (value or "").strip().lower() in TRUTHY_ENV_VALUES


def get_settings() -> Settings:
    """Read settings from environment variables.

    Missing API keys are intentionally allowed. Each Agent reports a clear
    provider-specific error so the Streamlit app can keep running.
    """

    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL),
        claude_model=os.getenv("CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL),
        gemini_model=os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL),
        demo_mode=is_truthy(os.getenv("DEMO_MODE")),
    )
