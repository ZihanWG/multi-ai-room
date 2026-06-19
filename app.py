"""Streamlit frontend for the multi AI discussion room."""

from __future__ import annotations

import streamlit as st

from agents import ClaudeAgent, CriticAgent, GeminiAgent, ModeratorAgent, OpenAIAgent


def render_agent_output(title: str, content: str) -> None:
    """Render a standard agent output block."""

    with st.container(border=True):
        st.subheader(title)
        st.markdown(content or "_无输出_")


def run_discussion(question: str) -> dict[str, str]:
    """Run all agents in the required order."""

    outputs: dict[str, str] = {}

    with st.spinner("GPT Agent 正在进行严谨分析..."):
        outputs["GPT Agent"] = OpenAIAgent().run(question)
    render_agent_output("GPT Agent：严谨分析", outputs["GPT Agent"])

    with st.spinner("Claude Agent 正在整理结构和风险..."):
        outputs["Claude Agent"] = ClaudeAgent().run(question)
    render_agent_output("Claude Agent：结构化表达与风险提示", outputs["Claude Agent"])

    with st.spinner("Gemini Agent 正在发散思考和比较方案..."):
        outputs["Gemini Agent"] = GeminiAgent().run(question)
    render_agent_output("Gemini Agent：发散思考与多方案比较", outputs["Gemini Agent"])

    with st.spinner("Critic Agent 正在批判性评审..."):
        outputs["Critic Agent"] = CriticAgent().run(
            question=question,
            gpt_answer=outputs["GPT Agent"],
            claude_answer=outputs["Claude Agent"],
            gemini_answer=outputs["Gemini Agent"],
        )
    render_agent_output("Critic Agent：批判性评审", outputs["Critic Agent"])

    with st.spinner("Moderator Agent 正在汇总最终结论..."):
        outputs["Moderator Agent"] = ModeratorAgent().run(
            question=question,
            gpt_answer=outputs["GPT Agent"],
            claude_answer=outputs["Claude Agent"],
            gemini_answer=outputs["Gemini Agent"],
            critic_answer=outputs["Critic Agent"],
        )

    st.markdown("## 最终结论")
    st.success(outputs["Moderator Agent"] or "Moderator Agent 无输出")

    return outputs


def main() -> None:
    """Render the Streamlit app."""

    st.set_page_config(page_title="多 AI 讨论室", page_icon="AI", layout="wide")
    st.title("多 AI 讨论室")
    st.caption("输入一个问题后，多个 AI Agent 会依次分析、批判并汇总最终建议。")

    question = st.text_area(
        label="请输入你的问题",
        placeholder="例如：我们是否应该把当前单体应用拆成微服务？",
        height=160,
    )

    if st.button("开始讨论", type="primary"):
        cleaned_question = question.strip()
        if not cleaned_question:
            st.warning("请先输入一个问题。")
            return

        run_discussion(cleaned_question)


if __name__ == "__main__":
    main()
