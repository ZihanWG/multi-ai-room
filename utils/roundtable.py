"""Helpers for visible cross-agent discussion rounds."""

from __future__ import annotations

from collections.abc import Mapping

from utils.conversation import truncate_text
from utils.prompts import (
    CURRENT_IDENTITY_MARKER,
    ORIGINAL_QUESTION_MARKER,
    PEER_RESPONSE_MARKER,
)

__all__ = ["PEER_RESPONSE_MARKER", "build_peer_response_prompt", "format_agent_blocks"]


def format_agent_blocks(
    outputs: Mapping[str, str],
    *,
    max_chars_per_agent: int | None = None,
) -> str:
    """Format named agent outputs for prompt context."""

    blocks = []
    for agent_name, content in outputs.items():
        cleaned_content = content.strip() or "无输出。"
        if max_chars_per_agent is not None:
            cleaned_content = truncate_text(cleaned_content, max_chars_per_agent)
        blocks.append(f"### {agent_name}\n{cleaned_content}")
    return "\n\n".join(blocks) or "无可用内容。"


def build_peer_response_prompt(
    *,
    agent_name: str,
    question: str,
    own_output: str,
    peer_outputs: Mapping[str, str],
    prior_responses: Mapping[str, str] | None = None,
    max_chars_per_agent: int | None = None,
) -> str:
    """Build a prompt that asks one agent to respond to peer agent outputs."""

    cleaned_own_output = own_output.strip() or "无输出。"
    if max_chars_per_agent is not None:
        cleaned_own_output = truncate_text(cleaned_own_output, max_chars_per_agent)

    prior_response_text = ""
    if prior_responses:
        prior_response_text = f"""

已出现的交叉回应：
{format_agent_blocks(prior_responses, max_chars_per_agent=max_chars_per_agent)}
""".rstrip()

    return f"""
{PEER_RESPONSE_MARKER}

{ORIGINAL_QUESTION_MARKER}
{question.strip()}

{CURRENT_IDENTITY_MARKER}
{agent_name}

你的首轮观点：
{cleaned_own_output}

其他 Agent 的首轮观点：
{format_agent_blocks(peer_outputs, max_chars_per_agent=max_chars_per_agent)}
{prior_response_text}

请进行一轮面向用户的交叉回应：
1. 明确回应其他 Agent 哪些观点你同意、不同意或需要补充。
2. 指出你基于他人观点修正了什么，或者坚持了什么。
3. 给出当前更可靠的建议。
4. 不要重复完整首轮回答，不要输出隐藏思维链。
输出语言为中文。
""".strip()
