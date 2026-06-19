"""Critic Agent that reviews the first three model answers."""

from __future__ import annotations

from openai import OpenAI

from agents.base import BaseAgent
from utils.config import get_settings


class CriticAgent(BaseAgent):
    """Agent responsible for critical review and disagreement analysis."""

    def __init__(self) -> None:
        super().__init__(
            name="Critic Agent",
            role_prompt=(
                "你是 Critic Agent，负责批判性评审前三个 Agent 的回答。"
                "你需要指出：哪些观点重复，哪些观点不严谨，哪些地方缺少证据，"
                "哪些结论过度自信，三个 Agent 的主要分歧是什么，哪些建议最值得保留。"
                "请输出面向用户的评审纪要，不要输出隐藏思维链。"
                "输出语言为中文。不要平均主义，要明确指出问题。"
            ),
        )
        self.settings = get_settings()

    def run(
        self,
        question: str,
        gpt_answer: str,
        claude_answer: str,
        gemini_answer: str,
    ) -> str:
        """Critique the GPT, Claude, and Gemini answers."""

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

请对前三个 Agent 的回答进行批判性评审。必须明确指出问题，不要为了平衡而平均分配优缺点。
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
