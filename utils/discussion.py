"""Pure helpers for assembling cross-agent discussion context.

These functions decide what each later stage (peer responses, Critic, Moderator)
sees. They have no Streamlit dependency, so they are unit-tested directly. A
failed agent output (missing key or call failure) is never quoted to other
agents as if it were real analysis — see [[utils.agent_errors]].
"""

from __future__ import annotations

from collections.abc import Mapping

from utils.agent_errors import is_failure_output

FIRST_ROUND_AGENT_KEYS = ("GPT Agent", "Claude Agent", "Gemini Agent")
CROSS_RESPONSE_AGENT_KEYS = (
    "GPT Agent 交叉回应",
    "Claude Agent 交叉回应",
    "Gemini Agent 交叉回应",
)


def get_peer_outputs(
    outputs: Mapping[str, str],
    *,
    current_agent_key: str,
) -> dict[str, str]:
    """Return usable first-round outputs from the other discussion agents."""

    return {
        agent_key: outputs[agent_key]
        for agent_key in FIRST_ROUND_AGENT_KEYS
        if agent_key != current_agent_key
        and agent_key in outputs
        and not is_failure_output(outputs[agent_key])
    }


def get_cross_response_outputs(outputs: Mapping[str, str]) -> dict[str, str]:
    """Return the usable peer-response outputs generated so far."""

    return {
        agent_key: outputs[agent_key]
        for agent_key in CROSS_RESPONSE_AGENT_KEYS
        if agent_key in outputs and not is_failure_output(outputs[agent_key])
    }


def build_review_context(outputs: Mapping[str, str]) -> str:
    """Build a compact context block for critic and moderator stages."""

    response_outputs = get_cross_response_outputs(outputs)
    if not response_outputs:
        return ""

    sections = [
        f"### {agent_name}\n{content.strip() or '无输出。'}"
        for agent_name, content in response_outputs.items()
    ]
    return "## GPT / Claude / Gemini 交叉回应记录\n\n" + "\n\n".join(sections)


def answer_for_review(outputs: Mapping[str, str], key: str) -> str:
    """Return an agent answer for Critic/Moderator, masking failed outputs.

    A failed output is replaced with a neutral note so the reviewer does not
    treat a missing-key or call-failure message as substantive content.
    """

    content = outputs.get(key, "")
    if is_failure_output(content):
        return f"（{key} 本轮未能产出有效回答，请在结论中忽略其内容）"
    return content
