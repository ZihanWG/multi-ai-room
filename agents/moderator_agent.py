"""Moderator Agent that produces the final synthesized answer."""

from __future__ import annotations

from agents.base import BaseAgent
from agents.provider_calls import (
    generate_with_provider,
    missing_any_provider_message,
    provider_env_var,
    resolve_provider_sequence,
)
from utils.agent_errors import call_failed_message, missing_key_message
from utils.config import get_settings
from utils.demo import build_demo_response
from utils.prompts import (
    CLAUDE_ANSWER_HEADER,
    GEMINI_ANSWER_HEADER,
    GPT_ANSWER_HEADER,
    ORIGINAL_QUESTION_MARKER,
)


class ModeratorAgent(BaseAgent):
    """Agent responsible for final synthesis and action recommendations."""

    def __init__(self) -> None:
        super().__init__(
            name="Moderator Agent",
            role_prompt=(
                "你是 Moderator Agent，负责整合所有观点，给出最终结论。"
                "你需要输出：问题拆解、各 Agent 观点摘要、主要分歧、最可靠判断、"
                "最终建议、下一步行动清单。输出语言为中文。结论要明确，不能只做简单总结。"
                "这是面向用户的汇总纪要，不要输出隐藏思维链。"
            ),
        )
        self.settings = get_settings()

    def run(
        self,
        question: str,
        gpt_answer: str,
        claude_answer: str,
        gemini_answer: str,
        critic_answer: str,
        peer_discussion: str = "",
    ) -> str:
        """Synthesize all agent outputs into a final conclusion."""

        if getattr(self.settings, "demo_mode", False):
            return build_demo_response(
                self.name,
                question,
                context="\n\n".join(
                    [
                        gpt_answer,
                        claude_answer,
                        gemini_answer,
                        peer_discussion,
                        critic_answer,
                    ]
                ),
            )

        prompt = f"""
{ORIGINAL_QUESTION_MARKER}
{question}

{GPT_ANSWER_HEADER}
{gpt_answer}

{CLAUDE_ANSWER_HEADER}
{claude_answer}

{GEMINI_ANSWER_HEADER}
{gemini_answer}

GPT / Claude / Gemini 交叉回应：
{peer_discussion or "无交叉回应记录。"}

Critic Agent 批判：
{critic_answer}

请整合以上首轮观点、交叉回应和 Critic 评审，给出明确的最终结论和可执行行动建议。
""".strip()

        provider_sequence = resolve_provider_sequence(
            self.settings,
            self.settings.moderator_provider,
        )
        if not provider_sequence:
            if self.settings.moderator_provider == "auto":
                return missing_any_provider_message()
            return missing_key_message(
                provider_env_var(self.settings.moderator_provider)
            )

        last_exception: Exception | None = None
        for provider in provider_sequence:
            try:
                return generate_with_provider(
                    settings=self.settings,
                    provider=provider,
                    system_prompt=self.role_prompt,
                    user_prompt=prompt,
                )
            except Exception as exc:
                last_exception = exc

        return call_failed_message(
            self.name,
            last_exception or RuntimeError("No provider produced a response."),
        )
