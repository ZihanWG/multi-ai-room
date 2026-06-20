"""Helpers for multi-turn discussion context."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


DEFAULT_CONTEXT_AGENT_ORDER = (
    "GPT Agent",
    "Claude Agent",
    "Gemini Agent",
    "GPT Agent 交叉回应",
    "Claude Agent 交叉回应",
    "Gemini Agent 交叉回应",
    "Critic Agent",
    "Moderator Agent",
)


def truncate_text(text: str, max_chars: int) -> str:
    """Return text truncated to a maximum number of characters."""

    cleaned = text.strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 20].rstrip() + "\n...（已截断）"


def coerce_outputs(value: object) -> dict[str, str]:
    """Convert a session-state output value into a string dictionary."""

    if not isinstance(value, Mapping):
        return {}

    return {
        str(agent_name): str(content)
        for agent_name, content in value.items()
        if agent_name is not None
    }


def build_follow_up_prompt(
    follow_up_question: str,
    turns: Sequence[Mapping[str, object]],
    *,
    max_turns: int = 3,
    max_chars_per_agent: int = 1200,
) -> str:
    """Build a contextual prompt for a follow-up question."""

    cleaned_follow_up = follow_up_question.strip()
    selected_turns = list(turns)[-max_turns:]
    history_blocks: list[str] = []

    for index, turn in enumerate(selected_turns, start=1):
        question = str(turn.get("question", "")).strip() or "未记录问题"
        outputs = coerce_outputs(turn.get("outputs"))
        output_lines = []

        for agent_name in DEFAULT_CONTEXT_AGENT_ORDER:
            if agent_name not in outputs:
                continue
            output_lines.append(
                f"### {agent_name}\n{truncate_text(outputs[agent_name], max_chars_per_agent)}"
            )

        history_blocks.append(
            "\n\n".join(
                [
                    f"## 历史第 {index} 轮",
                    f"用户问题：{question}",
                    "Agent 输出摘要：",
                    "\n\n".join(output_lines) or "无可用输出。",
                ]
            )
        )

    history = "\n\n---\n\n".join(history_blocks) or "暂无历史讨论。"

    return f"""
这是同一谈话窗口中的继续追问。请基于历史讨论回答用户的新问题，并避免重复已经明确的内容。

历史讨论：

{history}

用户新的追问：
{cleaned_follow_up}

请继续按当前 Agent 角色完成本轮回答。输出应面向用户，不要输出隐藏思维链。
""".strip()
