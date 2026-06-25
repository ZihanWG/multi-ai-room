"""OpenAI-powered GPT Agent."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

from openai import OpenAI

from agents.base import BaseAgent
from agents.provider_calls import build_openai_user_content
from utils.agent_errors import call_failed_message, missing_key_message
from utils.attachments import PreparedAttachment
from utils.config import get_settings
from utils.demo import build_demo_response


class OpenAIAgent(BaseAgent):
    """Agent responsible for rigorous analysis and logical reasoning."""

    def __init__(self) -> None:
        super().__init__(
            name="GPT Agent",
            role_prompt=(
                "你是 GPT Agent，负责严谨分析、逻辑推理、识别隐含假设、"
                "指出技术或决策中的关键问题。请输出面向用户的分析摘要，"
                "包含：一句话判断、关键依据、隐含假设、主要风险、建议。"
                "不要输出隐藏思维链。输出语言为中文。"
            ),
        )
        self.settings = get_settings()

    def run(
        self,
        question: str,
        attachments: Sequence[PreparedAttachment] | None = None,
    ) -> str:
        """Generate a GPT Agent response for the user's question."""

        if getattr(self.settings, "demo_mode", False):
            return build_demo_response(self.name, question)

        if not self.settings.openai_api_key:
            return missing_key_message("OPENAI_API_KEY")

        try:
            client = OpenAI(
                api_key=self.settings.openai_api_key,
                timeout=self.settings.request_timeout_seconds,
                max_retries=self.settings.provider_max_retries,
            )
            response = client.responses.create(
                model=self.settings.openai_model,
                input=cast(
                    Any,
                    [
                        {"role": "system", "content": self.role_prompt},
                        {
                            "role": "user",
                            "content": build_openai_user_content(
                                question,
                                attachments,
                            ),
                        },
                    ],
                ),
                max_output_tokens=self.settings.max_output_tokens,
            )
            return response.output_text.strip()
        except Exception as exc:
            return call_failed_message(self.name, exc)
