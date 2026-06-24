"""Google Gemini Agent."""

from __future__ import annotations

from google import genai
from google.genai import types

from agents.base import BaseAgent
from agents.provider_calls import gemini_retry_attempts
from utils.agent_errors import call_failed_message, missing_key_message
from utils.config import get_settings
from utils.demo import build_demo_response


class GeminiAgent(BaseAgent):
    """Agent responsible for divergent thinking and alternative paths."""

    def __init__(self) -> None:
        super().__init__(
            name="Gemini Agent",
            role_prompt=(
                "你是 Gemini Agent，负责发散思考、多方案比较、补充不同视角、"
                "提出替代路径。请输出面向用户的方案比较摘要，包含：可选路径、"
                "各自收益、代价、适用场景、推荐取舍。不要输出隐藏思维链。"
                "输出语言为中文。"
            ),
        )
        self.settings = get_settings()

    def run(self, question: str) -> str:
        """Generate a Gemini Agent response for the user's question."""

        if getattr(self.settings, "demo_mode", False):
            return build_demo_response(self.name, question)

        if not self.settings.gemini_api_key:
            return missing_key_message("GEMINI_API_KEY")

        try:
            client = genai.Client(
                api_key=self.settings.gemini_api_key,
                http_options=types.HttpOptions(
                    timeout=int(self.settings.request_timeout_seconds * 1000),
                    retry_options=types.HttpRetryOptions(
                        attempts=gemini_retry_attempts(
                            self.settings.provider_max_retries
                        ),
                    ),
                ),
            )
            response = client.models.generate_content(
                model=self.settings.gemini_model,
                contents=question,
                config=types.GenerateContentConfig(
                    system_instruction=self.role_prompt,
                    max_output_tokens=self.settings.max_output_tokens,
                ),
            )
            return (response.text or "").strip()
        except Exception as exc:
            return call_failed_message(self.name, exc)
