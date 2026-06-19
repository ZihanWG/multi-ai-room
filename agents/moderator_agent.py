"""Moderator Agent that produces the final synthesized answer."""

from __future__ import annotations

from openai import OpenAI

from agents.base import BaseAgent
from utils.config import get_settings


class ModeratorAgent(BaseAgent):
    """Agent responsible for final synthesis and action recommendations."""

    def __init__(self) -> None:
        super().__init__(
            name="Moderator Agent",
            role_prompt=(
                "你是 Moderator Agent，负责整合所有观点，给出最终结论。"
                "你需要输出：问题拆解、各 Agent 观点摘要、主要分歧、最可靠判断、"
                "最终建议、下一步行动清单。输出语言为中文。结论要明确，不能只做简单总结。"
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
    ) -> str:
        """Synthesize all agent outputs into a final conclusion."""

        if not self.settings.openai_api_key:
            return "缺少 OPENAI_API_KEY，请在 .env 文件中配置。"

        prompt = f"""
用户原始问题：
{question}

GPT Agent 回答：
{gpt_answer}

Claude Agent 回答：
{claude_answer}

Gemini Agent 回答：
{gemini_answer}

Critic Agent 批判：
{critic_answer}

请整合以上内容，给出明确的最终结论和可执行行动建议。
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
            return f"{self.name} 调用失败：{exc}"
