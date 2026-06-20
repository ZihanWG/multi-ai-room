"""Helpers for visible cross-agent discussion rounds."""

from __future__ import annotations

from collections.abc import Mapping


PEER_RESPONSE_MARKER = "交叉回应任务"


def format_agent_blocks(outputs: Mapping[str, str]) -> str:
    """Format named agent outputs for prompt context."""

    blocks = []
    for agent_name, content in outputs.items():
        cleaned_content = content.strip() or "无输出。"
        blocks.append(f"### {agent_name}\n{cleaned_content}")
    return "\n\n".join(blocks) or "无可用内容。"


def build_peer_response_prompt(
    *,
    agent_name: str,
    question: str,
    own_output: str,
    peer_outputs: Mapping[str, str],
    prior_responses: Mapping[str, str] | None = None,
) -> str:
    """Build a prompt that asks one agent to respond to peer agent outputs."""

    prior_response_text = ""
    if prior_responses:
        prior_response_text = f"""

已出现的交叉回应：
{format_agent_blocks(prior_responses)}
""".rstrip()

    return f"""
{PEER_RESPONSE_MARKER}

用户原始问题：
{question.strip()}

你当前身份：
{agent_name}

你的首轮观点：
{own_output.strip() or "无输出。"}

其他 Agent 的首轮观点：
{format_agent_blocks(peer_outputs)}
{prior_response_text}

请进行一轮面向用户的交叉回应：
1. 明确回应其他 Agent 哪些观点你同意、不同意或需要补充。
2. 指出你基于他人观点修正了什么，或者坚持了什么。
3. 给出当前更可靠的建议。
4. 不要重复完整首轮回答，不要输出隐藏思维链。
输出语言为中文。
""".strip()
