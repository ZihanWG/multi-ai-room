"""Anthropic Claude Agent."""

from __future__ import annotations

from anthropic import Anthropic

from agents.base import BaseAgent
from utils.config import get_settings
from utils.demo import build_demo_response


class ClaudeAgent(BaseAgent):
    """Agent responsible for structure, risks, and conservative judgment."""

    def __init__(self) -> None:
        super().__init__(
            name="Claude Agent",
            role_prompt=(
                "你是 Claude Agent，负责结构化表达、风险提示、文字清晰度、"
                "方案可读性和保守判断。请输出面向用户的讨论纪要，包含："
                "结构化拆解、限制条件、风险清单、保守建议。不要输出隐藏思维链。"
                "输出语言为中文。"
            ),
        )
        self.settings = get_settings()

    def run(self, question: str) -> str:
        """Generate a Claude Agent response for the user's question."""

        if self.settings.demo_mode:
            return build_demo_response(self.name, question)

        if not self.settings.anthropic_api_key:
            return "缺少 ANTHROPIC_API_KEY，请在 .env 文件中配置。"

        try:
            client = Anthropic(api_key=self.settings.anthropic_api_key)
            response = client.messages.create(
                model=self.settings.claude_model,
                max_tokens=1200,
                system=self.role_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": question,
                    }
                ],
            )
            return "".join(
                block.text for block in response.content if block.type == "text"
            ).strip()
        except Exception as exc:
            return f"{self.name} 调用失败：{exc}"
