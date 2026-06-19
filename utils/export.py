"""Helpers for exporting discussion results."""

from __future__ import annotations

from collections.abc import Mapping, Sequence


DEFAULT_AGENT_ORDER = (
    "GPT Agent",
    "Claude Agent",
    "Gemini Agent",
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
