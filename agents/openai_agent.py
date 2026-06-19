"""OpenAI-powered GPT Agent."""

from __future__ import annotations

from openai import OpenAI

from agents.base import BaseAgent
from utils.config import get_settings


class OpenAIAgent(BaseAgent):
    """Agent responsible for rigorous analysis and logical reasoning."""

    def __init__(self) -> None:
        super().__init__(
            name="GPT Agent",
            role_prompt=(
                "你是 GPT Agent，负责严谨分析、逻辑推理、识别隐含假设、"
                "指出技术或决策中的关键问题。输出语言为中文。"
            ),
        )
        self.settings = get_settings()

    def run(self, question: str) -> str:
        """Generate a GPT Agent response for the user's question."""

        if not self.settings.openai_api_key:
            return "缺少 OPENAI_API_KEY，请在 .env 文件中配置。"

        try:
            client = OpenAI(api_key=self.settings.openai_api_key)
            response = client.responses.create(
                model=self.settings.openai_model,
                input=[
                    {"role": "system", "content": self.role_prompt},
                    {"role": "user", "content": question},
                ],
            )
            return response.output_text.strip()
        except Exception as exc:
            return f"{self.name} 调用失败：{exc}"
