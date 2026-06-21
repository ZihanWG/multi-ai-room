"""Moderator Agent that produces the final synthesized answer."""

from __future__ import annotations

from openai import OpenAI

from agents.base import BaseAgent
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

        if not self.settings.openai_api_key:
            return missing_key_message("OPENAI_API_KEY")

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

        try:
            client = OpenAI(api_key=self.settings.openai_api_key)
            response = client.responses.create(
                model=self.settings.openai_model,
                input=[
                    {"role": "system", "content": self.role_prompt},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.output_text.strip()
        except Exception as exc:
            return call_failed_message(self.name, exc)
