"""Shared agent failure messages and detection.

Agents intentionally return error strings instead of raising, so a single
provider failure does not crash the whole discussion. These helpers keep the
exact wording in one place and let the orchestrator recognize a failed output
so it is not fed into downstream agent prompts as if it were real analysis.
"""

from __future__ import annotations

MISSING_KEY_SUFFIX = "，请在 .env 文件中配置。"
CALL_FAILED_MARKER = "调用失败："


def missing_key_message(env_var: str) -> str:
    """Return the standard message for a missing provider API key."""

    return f"缺少 {env_var}{MISSING_KEY_SUFFIX}"


def call_failed_message(agent_name: str, exc: object) -> str:
    """Return the standard message for a failed provider call."""

    return f"{agent_name} {CALL_FAILED_MARKER}{exc}"


def is_failure_output(text: str) -> bool:
    """Return whether an agent output is a missing-key or call-failure message."""

    return MISSING_KEY_SUFFIX in text or CALL_FAILED_MARKER in text
