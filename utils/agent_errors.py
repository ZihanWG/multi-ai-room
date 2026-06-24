"""Shared agent failure messages and detection.

Agents intentionally return error strings instead of raising, so a single
provider failure does not crash the whole discussion. These helpers keep the
exact wording in one place and let the orchestrator recognize a failed output
so it is not fed into downstream agent prompts as if it were real analysis.
"""

from __future__ import annotations

MISSING_KEY_SUFFIX = "，请在 .env 文件中配置。"
CALL_FAILED_MARKER = "调用失败："


def classify_exception(exc: object) -> str:
    """Return a user-safe failure category without exposing raw exception text."""

    exc_name = type(exc).__name__.lower()
    exc_text = str(exc).lower()
    combined = f"{exc_name} {exc_text}"

    if (
        isinstance(exc, TimeoutError)
        or "timeout" in combined
        or "timed out" in combined
    ):
        return "请求超时，请稍后重试或调低模型输出长度。"
    if (
        "authentication" in combined
        or "unauthorized" in combined
        or "api key" in combined
    ):
        return "认证失败，请检查 API Key 配置。"
    if "rate" in combined or "429" in combined or "quota" in combined:
        return "请求被限流或额度不足，请稍后重试。"
    if "connect" in combined or "network" in combined or "dns" in combined:
        return "网络连接失败，请检查网络或服务商状态。"
    return "服务商返回错误，请稍后重试。"


def missing_key_message(env_var: str) -> str:
    """Return the standard message for a missing provider API key."""

    return f"缺少 {env_var}{MISSING_KEY_SUFFIX}"


def call_failed_message(agent_name: str, exc: object) -> str:
    """Return the standard message for a failed provider call."""

    return f"{agent_name} {CALL_FAILED_MARKER}{classify_exception(exc)}"


def is_failure_output(text: str) -> bool:
    """Return whether an agent output is a missing-key or call-failure message."""

    return MISSING_KEY_SUFFIX in text or CALL_FAILED_MARKER in text
