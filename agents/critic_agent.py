"""Critic Agent that reviews the first three model answers."""

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
        peer_discussion: str = "",
    ) -> str:
        """Critique the GPT, Claude, and Gemini answers."""

        if getattr(self.settings, "demo_mode", False):
            return build_demo_response(
                self.name,
                question,
                context="\n\n".join(
                    [gpt_answer, claude_answer, gemini_answer, peer_discussion]
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

请对前三个 Agent 的首轮回答和交叉回应进行批判性评审。必须明确指出问题，不要为了平衡而平均分配优缺点。
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
