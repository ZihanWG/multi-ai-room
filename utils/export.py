"""Helpers for exporting discussion results."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from utils.conversation import coerce_outputs


DEFAULT_AGENT_ORDER = (
    "GPT Agent",
    "Claude Agent",
    "Gemini Agent",
    "GPT Agent 交叉回应",
    "Claude Agent 交叉回应",
    "Gemini Agent 交叉回应",
    "Critic Agent",
    "Moderator Agent",
)


def build_discussion_markdown(
    question: str,
    outputs: Mapping[str, str],
    *,
    agent_order: Sequence[str] = DEFAULT_AGENT_ORDER,
) -> str:
    """Build a Markdown document from a discussion result."""

    lines = [
        "# 多 AI 讨论室结果 / Multi AI Discussion Result",
        "",
        "## 原始问题 / Original Question",
        "",
        question.strip() or "_未记录原始问题 / Original question not recorded_",
        "",
        "## Agent 输出 / Agent Outputs",
        "",
    ]

    rendered_agents = set()
    for agent_name in agent_order:
        if agent_name not in outputs:
            continue
        rendered_agents.add(agent_name)
        lines.extend(
            [
                f"### {agent_name}",
                "",
                outputs[agent_name].strip() or "_无输出 / No output_",
                "",
            ]
        )

    for agent_name, content in outputs.items():
        if agent_name in rendered_agents:
            continue
        lines.extend(
            [
                f"### {agent_name}",
                "",
                content.strip() or "_无输出 / No output_",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def build_conversation_markdown(
    turns: Sequence[Mapping[str, object]],
    *,
    agent_order: Sequence[str] = DEFAULT_AGENT_ORDER,
) -> str:
    """Build a Markdown document from a multi-turn conversation."""

    lines = [
        "# 多 AI 讨论室对话记录 / Multi AI Discussion Conversation",
        "",
    ]

    if not turns:
        lines.extend(["_暂无对话记录 / No conversation turns recorded_", ""])
        return "\n".join(lines).rstrip() + "\n"

    for index, turn in enumerate(turns, start=1):
        question = str(turn.get("question", "")).strip()
        outputs = coerce_outputs(turn.get("outputs"))
        lines.extend(
            [
                f"## 第 {index} 轮 / Turn {index}",
                "",
                "### 问题 / Question",
                "",
                question or "_未记录问题 / Question not recorded_",
                "",
                "### Agent 输出 / Agent Outputs",
                "",
            ]
        )

        rendered_agents = set()
        for agent_name in agent_order:
            if agent_name not in outputs:
                continue
            rendered_agents.add(agent_name)
            lines.extend(
                [
                    f"#### {agent_name}",
                    "",
                    outputs[agent_name].strip() or "_无输出 / No output_",
                    "",
                ]
            )

        for agent_name, content in outputs.items():
            if agent_name in rendered_agents:
                continue
            lines.extend(
                [
                    f"#### {agent_name}",
                    "",
                    content.strip() or "_无输出 / No output_",
                    "",
                ]
            )

    return "\n".join(lines).rstrip() + "\n"
