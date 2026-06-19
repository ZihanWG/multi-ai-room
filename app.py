"""Streamlit frontend for the multi AI discussion room."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import streamlit as st

from agents import ClaudeAgent, CriticAgent, GeminiAgent, ModeratorAgent, OpenAIAgent


@dataclass(frozen=True)
class AgentProfile:
    """UI metadata for a discussion agent."""

    key: str
    title: str
    role: str
    objective: str
    input_note: str
    spinner: str
    accent: str


AGENT_PROFILES = [
    AgentProfile(
        key="GPT Agent",
        title="GPT Agent",
        role="严谨分析",
        objective="拆解问题、识别隐含假设，并给出第一版判断。",
        input_note="用户原始问题",
        spinner="GPT Agent 正在进行严谨分析...",
        accent="#2563eb",
    ),
    AgentProfile(
        key="Claude Agent",
        title="Claude Agent",
        role="结构与风险",
        objective="整理表达结构，补充风险、限制条件和保守判断。",
        input_note="用户原始问题",
        spinner="Claude Agent 正在整理结构和风险...",
        accent="#0f766e",
    ),
    AgentProfile(
        key="Gemini Agent",
        title="Gemini Agent",
        role="发散比较",
        objective="提出替代路径，比较不同方案的收益和代价。",
        input_note="用户原始问题",
        spinner="Gemini Agent 正在发散思考和比较方案...",
        accent="#65a30d",
    ),
    AgentProfile(
        key="Critic Agent",
        title="Critic Agent",
        role="批判评审",
        objective="审查前三个回答的漏洞、重复、证据不足和过度自信。",
        input_note="用户问题 + GPT/Claude/Gemini 的回答",
        spinner="Critic Agent 正在批判性评审...",
        accent="#dc2626",
    ),
    AgentProfile(
        key="Moderator Agent",
        title="Moderator Agent",
        role="最终汇总",
        objective="整合分歧和共识，输出明确结论与下一步行动。",
        input_note="用户问题 + 所有 Agent 的回答与评审",
        spinner="Moderator Agent 正在汇总最终结论...",
        accent="#0891b2",
    ),
]


def get_profile(key: str) -> AgentProfile:
    """Return the UI profile for an agent key."""

    return next(profile for profile in AGENT_PROFILES if profile.key == key)


def apply_page_styles() -> None:
    """Apply lightweight visual styling for the Streamlit app."""

    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(20, 184, 166, 0.12), transparent 34rem),
                linear-gradient(135deg, #f8fbfa 0%, #eef8f6 42%, #ffffff 100%);
        }

        [data-testid="stSidebar"] {
            background: #f7fbfa;
            border-right: 1px solid #dbe7e4;
        }

        .hero {
            padding: 2rem 2.2rem;
            margin-bottom: 1.4rem;
            border: 1px solid #dbe7e4;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.82);
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
        }

        .hero-eyebrow {
            color: #0f766e;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .hero h1 {
            margin: 0.35rem 0 0.45rem;
            color: #0f172a;
            font-size: 2.2rem;
            line-height: 1.15;
        }

        .hero p {
            max-width: 52rem;
            margin: 0;
            color: #475569;
            font-size: 1.02rem;
            line-height: 1.7;
        }

        .agent-card,
        .timeline-card,
        .final-card {
            border: 1px solid #dbe7e4;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.9);
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
        }

        .agent-card {
            min-height: 12.5rem;
            padding: 1rem;
            border-top: 4px solid var(--accent-color);
        }

        .agent-title {
            color: #0f172a;
            font-size: 1rem;
            font-weight: 750;
            margin-bottom: 0.25rem;
        }

        .agent-role {
            color: #0f766e;
            font-size: 0.86rem;
            font-weight: 650;
            margin-bottom: 0.75rem;
        }

        .agent-objective {
            color: #475569;
            font-size: 0.9rem;
            line-height: 1.55;
        }

        .timeline-card {
            padding: 0.95rem;
            border-left: 5px solid #cbd5e1;
        }

        .timeline-card.is-active {
            border-left-color: #0f766e;
            background: #f0fdfa;
        }

        .timeline-card.is-done {
            border-left-color: #14b8a6;
        }

        .timeline-index {
            display: inline-flex;
            width: 1.65rem;
            height: 1.65rem;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            color: white;
            background: #0f766e;
            font-size: 0.82rem;
            font-weight: 750;
            margin-right: 0.45rem;
        }

        .timeline-title {
            color: #0f172a;
            font-weight: 750;
        }

        .timeline-meta,
        .timeline-state {
            margin-top: 0.45rem;
            color: #64748b;
            font-size: 0.86rem;
            line-height: 1.5;
        }

        .status-pill {
            display: inline-block;
            padding: 0.18rem 0.55rem;
            border-radius: 999px;
            background: #e6fffb;
            color: #0f766e;
            font-size: 0.78rem;
            font-weight: 700;
        }

        .final-card {
            padding: 1.2rem 1.35rem;
            border-left: 6px solid #0891b2;
            background: #f0f9ff;
        }

        div[data-testid="stButton"] > button {
            border-radius: 999px;
            padding: 0.65rem 1.25rem;
            font-weight: 750;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    """Render the top-level product header."""

    st.markdown(
        """
        <section class="hero">
            <div class="hero-eyebrow">Multi AI Discussion Room</div>
            <h1>多 AI 讨论室</h1>
            <p>
                输入一个问题后，不同角色的 AI 会依次分析、补充、批判和汇总。
                页面会展示面向用户的讨论纪要、阶段状态和最终行动建议。
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_agent_board() -> None:
    """Render the static role board for all discussion agents."""

    st.markdown("### 讨论席位")
    columns = st.columns(len(AGENT_PROFILES))
    for column, profile in zip(columns, AGENT_PROFILES, strict=True):
        with column:
            st.markdown(
                f"""
                <div class="agent-card" style="--accent-color: {profile.accent};">
                    <div class="agent-title">{profile.title}</div>
                    <div class="agent-role">{profile.role}</div>
                    <div class="agent-objective">{profile.objective}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_agent_output(
    profile: AgentProfile,
    content: str,
    *,
    expanded: bool,
) -> None:
    """Render a standard agent output block."""

    with st.container(border=True):
        header, state = st.columns([0.78, 0.22])
        with header:
            st.subheader(f"{profile.title}：{profile.role}")
            st.caption(profile.objective)
        with state:
            st.markdown('<span class="status-pill">已完成</span>', unsafe_allow_html=True)

        st.markdown(f"**本轮输入**：{profile.input_note}")
        if expanded:
            st.markdown(content or "_无输出_")
        else:
            with st.expander("查看完整输出", expanded=False):
                st.markdown(content or "_无输出_")


def render_discussion_timeline(
    placeholder: st.delta_generator.DeltaGenerator,
    outputs: dict[str, str],
    active_key: str | None,
) -> None:
    """Render the visible discussion process timeline."""

    with placeholder.container():
        st.markdown("### 讨论过程")
        st.caption(
            "这里展示的是各 Agent 的阶段发言、输入来源和可读分析摘要；"
            "不展示模型内部隐藏思维链。"
        )

        columns = st.columns(len(AGENT_PROFILES))
        for index, (column, profile) in enumerate(
            zip(columns, AGENT_PROFILES, strict=True),
            start=1,
        ):
            if profile.key in outputs:
                state_label = "已完成"
                state_class = "is-done"
            elif profile.key == active_key:
                state_label = "进行中"
                state_class = "is-active"
            else:
                state_label = "等待中"
                state_class = ""

            with column:
                st.markdown(
                    f"""
                    <div class="timeline-card {state_class}">
                        <div>
                            <span class="timeline-index">{index}</span>
                            <span class="timeline-title">{profile.title}</span>
                        </div>
                        <div class="timeline-meta">{profile.role}</div>
                        <div class="timeline-state">{state_label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        for profile in AGENT_PROFILES:
            expanded = profile.key == active_key or profile.key in outputs
            with st.expander(f"{profile.title} 过程记录", expanded=expanded):
                st.markdown(f"**本轮职责**：{profile.objective}")
                st.markdown(f"**输入来源**：{profile.input_note}")
                if profile.key == active_key:
                    st.info("当前正在生成这一轮发言。")
                elif profile.key in outputs:
                    st.markdown("**阶段输出**")
                    st.markdown(outputs[profile.key] or "_无输出_")
                else:
                    st.caption("等待前置 Agent 完成后开始。")


def render_summary_panel(outputs: dict[str, str]) -> None:
    """Render a compact status summary after a run."""

    done_count = sum(1 for profile in AGENT_PROFILES if profile.key in outputs)
    failed_count = sum("调用失败" in output or "缺少" in output for output in outputs.values())
    final_ready = bool(outputs.get("Moderator Agent"))

    columns = st.columns(3)
    columns[0].metric("已完成回合", f"{done_count}/{len(AGENT_PROFILES)}")
    columns[1].metric("需要检查", f"{failed_count}")
    columns[2].metric("最终结论", "已生成" if final_ready else "未生成")


def render_final_answer(content: str) -> None:
    """Render the final moderator answer as the most prominent result."""

    st.markdown("## 最终结论")
    with st.container(border=True):
        st.markdown(
            '<span class="status-pill">Moderator Agent 汇总</span>',
            unsafe_allow_html=True,
        )
        st.markdown(content or "Moderator Agent 无输出")


def render_sidebar_controls() -> tuple[bool, bool]:
    """Render sidebar options and return UI preferences."""

    with st.sidebar:
        st.header("显示设置")
        show_process = st.toggle("显示讨论过程", value=True)
        expand_outputs = st.toggle("默认展开 Agent 原文", value=True)

        st.divider()
        st.markdown("#### 说明")
        st.caption(
            "讨论过程是面向用户的阶段记录和分析摘要，用于理解各 Agent 如何分工。"
            "它不是模型的隐藏思维链。"
        )

        st.divider()
        st.markdown("#### 调用顺序")
        for index, profile in enumerate(AGENT_PROFILES, start=1):
            st.markdown(f"{index}. **{profile.title}**：{profile.role}")

    return show_process, expand_outputs


def run_agent_step(
    profile: AgentProfile,
    runner: Callable[[], str],
    outputs: dict[str, str],
    timeline_placeholder: st.delta_generator.DeltaGenerator,
    progress_bar: st.delta_generator.DeltaGenerator,
    step_index: int,
    *,
    show_process: bool,
    expand_outputs: bool,
) -> None:
    """Run one agent, update progress, and render its result."""

    if show_process:
        render_discussion_timeline(timeline_placeholder, outputs, active_key=profile.key)

    with st.spinner(profile.spinner):
        outputs[profile.key] = runner()

    progress_bar.progress(
        step_index / len(AGENT_PROFILES),
        text=f"已完成：{profile.title}",
    )

    if show_process:
        render_discussion_timeline(timeline_placeholder, outputs, active_key=None)

    render_agent_output(profile, outputs[profile.key], expanded=expand_outputs)


def run_discussion(
    question: str,
    *,
    show_process: bool,
    expand_outputs: bool,
) -> dict[str, str]:
    """Run all agents in the required order."""

    outputs: dict[str, str] = {}
    progress_bar = st.progress(0, text="准备开始讨论")
    timeline_placeholder = st.empty()

    if show_process:
        render_discussion_timeline(timeline_placeholder, outputs, active_key=None)

    run_agent_step(
        get_profile("GPT Agent"),
        lambda: OpenAIAgent().run(question),
        outputs,
        timeline_placeholder,
        progress_bar,
        1,
        show_process=show_process,
        expand_outputs=expand_outputs,
    )
    run_agent_step(
        get_profile("Claude Agent"),
        lambda: ClaudeAgent().run(question),
        outputs,
        timeline_placeholder,
        progress_bar,
        2,
        show_process=show_process,
        expand_outputs=expand_outputs,
    )
    run_agent_step(
        get_profile("Gemini Agent"),
        lambda: GeminiAgent().run(question),
        outputs,
        timeline_placeholder,
        progress_bar,
        3,
        show_process=show_process,
        expand_outputs=expand_outputs,
    )
    run_agent_step(
        get_profile("Critic Agent"),
        lambda: CriticAgent().run(
            question=question,
            gpt_answer=outputs["GPT Agent"],
            claude_answer=outputs["Claude Agent"],
            gemini_answer=outputs["Gemini Agent"],
        ),
        outputs,
        timeline_placeholder,
        progress_bar,
        4,
        show_process=show_process,
        expand_outputs=expand_outputs,
    )
    run_agent_step(
        get_profile("Moderator Agent"),
        lambda: ModeratorAgent().run(
            question=question,
            gpt_answer=outputs["GPT Agent"],
            claude_answer=outputs["Claude Agent"],
            gemini_answer=outputs["Gemini Agent"],
            critic_answer=outputs["Critic Agent"],
        ),
        outputs,
        timeline_placeholder,
        progress_bar,
        5,
        show_process=show_process,
        expand_outputs=expand_outputs,
    )

    render_summary_panel(outputs)
    render_final_answer(outputs["Moderator Agent"])

    return outputs


def main() -> None:
    """Render the Streamlit app."""

    st.set_page_config(page_title="多 AI 讨论室", page_icon="AI", layout="wide")
    apply_page_styles()
    show_process, expand_outputs = render_sidebar_controls()
    render_hero()
    render_agent_board()

    st.markdown("### 开始一次讨论")
    input_column, guide_column = st.columns([0.66, 0.34], gap="large")
    with input_column:
        question = st.text_area(
            label="请输入你的问题",
            placeholder="例如：我们是否应该把当前单体应用拆成微服务？",
            height=180,
        )
    with guide_column:
        with st.container(border=True):
            st.markdown("#### 本次流程")
            st.markdown(
                """
                1. GPT 先做严谨拆解
                2. Claude 补充结构和风险
                3. Gemini 给出替代方案
                4. Critic 评审前三轮回答
                5. Moderator 汇总为最终建议
                """
            )

    if st.button("开始讨论", type="primary"):
        cleaned_question = question.strip()
        if not cleaned_question:
            st.warning("请先输入一个问题。")
            return

        run_discussion(
            cleaned_question,
            show_process=show_process,
            expand_outputs=expand_outputs,
        )


if __name__ == "__main__":
    main()
