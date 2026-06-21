"""Streamlit frontend for the multi AI discussion room."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

import streamlit as st

from agents import ClaudeAgent, CriticAgent, GeminiAgent, ModeratorAgent, OpenAIAgent
from styles import apply_page_styles
from utils.config import get_settings
from utils.conversation import build_follow_up_prompt, coerce_outputs
from utils.discussion import (
    answer_for_review,
    build_review_context,
    get_cross_response_outputs,
    get_peer_outputs,
)
from utils.export import build_conversation_markdown, build_discussion_markdown
from utils.roundtable import build_peer_response_prompt


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

DISCUSSION_STAGES = [
    AGENT_PROFILES[0],
    AGENT_PROFILES[1],
    AGENT_PROFILES[2],
    AgentProfile(
        key="GPT Agent 交叉回应",
        title="GPT Agent 回应",
        role="回应分歧",
        objective="读取 Claude 和 Gemini 的观点，说明同意、分歧和修正后的判断。",
        input_note="用户问题 + GPT 首轮观点 + Claude/Gemini 首轮观点",
        spinner="GPT Agent 正在回应 Claude 和 Gemini...",
        accent="#1d4ed8",
    ),
    AgentProfile(
        key="Claude Agent 交叉回应",
        title="Claude Agent 回应",
        role="结构复议",
        objective="读取 GPT/Gemini 的观点和前一轮回应，补充结构、风险和限制条件。",
        input_note="用户问题 + Claude 首轮观点 + GPT/Gemini 观点 + GPT 回应",
        spinner="Claude Agent 正在回应 GPT 和 Gemini...",
        accent="#0d9488",
    ),
    AgentProfile(
        key="Gemini Agent 交叉回应",
        title="Gemini Agent 回应",
        role="方案复议",
        objective="读取 GPT/Claude 的观点和回应，补充替代路径与取舍判断。",
        input_note="用户问题 + Gemini 首轮观点 + GPT/Claude 观点与回应",
        spinner="Gemini Agent 正在回应 GPT 和 Claude...",
        accent="#4d7c0f",
    ),
    AGENT_PROFILES[3],
    AGENT_PROFILES[4],
]

SESSION_OUTPUTS_KEY = "discussion_outputs"
SESSION_QUESTION_KEY = "discussion_question"
SESSION_TURNS_KEY = "discussion_turns"


def get_profile(key: str) -> AgentProfile:
    """Return the UI profile for an agent key."""

    return next(profile for profile in DISCUSSION_STAGES if profile.key == key)


def get_discussion_stage_keys() -> list[str]:
    """Return the visible stage order for a full discussion."""

    return [profile.key for profile in DISCUSSION_STAGES]


def initialize_session_state() -> None:
    """Initialize Streamlit session state used across reruns."""

    if SESSION_OUTPUTS_KEY not in st.session_state:
        st.session_state[SESSION_OUTPUTS_KEY] = {}
    if SESSION_QUESTION_KEY not in st.session_state:
        st.session_state[SESSION_QUESTION_KEY] = ""
    if SESSION_TURNS_KEY not in st.session_state:
        st.session_state[SESSION_TURNS_KEY] = []

    if (
        not st.session_state[SESSION_TURNS_KEY]
        and st.session_state[SESSION_OUTPUTS_KEY]
    ):
        st.session_state[SESSION_TURNS_KEY].append(
            {
                "question": st.session_state[SESSION_QUESTION_KEY],
                "outputs": st.session_state[SESSION_OUTPUTS_KEY],
            }
        )


def get_discussion_turns() -> list[dict[str, object]]:
    """Return the current in-session discussion turns."""

    return st.session_state[SESSION_TURNS_KEY]


def save_discussion_turn(question: str, outputs: dict[str, str]) -> None:
    """Persist one discussion turn in Streamlit session state."""

    stored_outputs = outputs.copy()
    st.session_state[SESSION_QUESTION_KEY] = question
    st.session_state[SESSION_OUTPUTS_KEY] = stored_outputs
    st.session_state[SESSION_TURNS_KEY].append(
        {
            "question": question,
            "outputs": stored_outputs,
        }
    )


def render_hero() -> None:
    """Render the top-level product header."""

    st.markdown(
        """
        <section class="hero">
            <div class="hero-eyebrow">Multi AI Discussion Room</div>
            <h1>多 AI 讨论室</h1>
            <p>
                输入一个问题后，GPT、Claude 和 Gemini 会先给出观点，再互相回应。
                页面会展示面向用户的讨论纪要、交叉回应、阶段状态和最终行动建议。
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
            st.markdown(
                '<span class="status-pill">已完成</span>', unsafe_allow_html=True
            )

        st.markdown(f"**本轮输入**：{profile.input_note}")
        if expanded:
            st.markdown(content or "_无输出_")
        else:
            with st.expander("查看完整输出", expanded=False):
                st.markdown(content or "_无输出_")


def render_discussion_timeline(
    placeholder: st.delta_generator.DeltaGenerator,
    outputs: dict[str, str],
    active_keys: set[str] | None,
) -> None:
    """Render the visible discussion process timeline.

    ``active_keys`` may hold more than one stage so the parallel first round
    can show all three agents as 进行中 at once.
    """

    active = active_keys or set()
    with placeholder.container():
        st.markdown("### 讨论过程")
        st.caption(
            "这里展示首轮观点、Agent 之间的交叉回应、批判评审和最终汇总；"
            "不展示模型内部隐藏思维链。"
        )

        for row_start in range(0, len(DISCUSSION_STAGES), 4):
            row_profiles = DISCUSSION_STAGES[row_start : row_start + 4]
            columns = st.columns(len(row_profiles))
            for offset, (column, profile) in enumerate(
                zip(columns, row_profiles, strict=True),
                start=1,
            ):
                index = row_start + offset
                if profile.key in outputs:
                    state_label = "已完成"
                    state_class = "is-done"
                elif profile.key in active:
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

        for profile in DISCUSSION_STAGES:
            expanded = profile.key in active or profile.key in outputs
            with st.expander(f"{profile.title} 过程记录", expanded=expanded):
                st.markdown(f"**本轮职责**：{profile.objective}")
                st.markdown(f"**输入来源**：{profile.input_note}")
                if profile.key in active:
                    st.info("当前正在生成这一轮发言。")
                elif profile.key in outputs:
                    st.markdown("**阶段输出**")
                    st.markdown(outputs[profile.key] or "_无输出_")
                else:
                    st.caption("等待前置 Agent 完成后开始。")


def render_summary_panel(outputs: dict[str, str]) -> None:
    """Render a compact status summary after a run."""

    done_count = sum(1 for profile in DISCUSSION_STAGES if profile.key in outputs)
    failed_count = sum(
        "调用失败" in output or "缺少" in output for output in outputs.values()
    )
    final_ready = bool(outputs.get("Moderator Agent"))

    columns = st.columns(3)
    columns[0].metric("已完成阶段", f"{done_count}/{len(DISCUSSION_STAGES)}")
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


def render_export_button(question: str, outputs: dict[str, str], *, key: str) -> None:
    """Render a Markdown download button for a discussion result."""

    if not outputs:
        return

    st.download_button(
        label="导出 Markdown",
        data=build_discussion_markdown(
            question,
            outputs,
            agent_order=get_discussion_stage_keys(),
        ),
        file_name="multi-ai-room-discussion.md",
        mime="text/markdown",
        key=key,
    )


def render_conversation_export_button(
    turns: list[dict[str, object]],
    *,
    key: str,
) -> None:
    """Render a Markdown download button for the whole conversation."""

    if not turns:
        return

    st.download_button(
        label="导出整段对话 Markdown",
        data=build_conversation_markdown(
            turns,
            agent_order=get_discussion_stage_keys(),
        ),
        file_name="multi-ai-room-conversation.md",
        mime="text/markdown",
        key=key,
    )


def render_discussion_result(
    title: str,
    question: str,
    outputs: dict[str, str],
    *,
    show_process: bool,
    expand_outputs: bool,
    export_key: str,
) -> None:
    """Render one completed discussion result."""

    if not outputs:
        return

    st.markdown(title)
    with st.container(border=True):
        st.markdown("**原始问题**")
        st.markdown(question or "_未记录原始问题_")

    if show_process:
        timeline_placeholder = st.empty()
        render_discussion_timeline(timeline_placeholder, outputs, active_keys=None)

    for profile in DISCUSSION_STAGES:
        if profile.key in outputs:
            render_agent_output(
                profile,
                outputs[profile.key],
                expanded=expand_outputs,
            )

    render_summary_panel(outputs)
    render_final_answer(outputs.get("Moderator Agent", ""))
    render_export_button(question, outputs, key=export_key)


def render_conversation_history(
    turns: list[dict[str, object]],
    *,
    show_process: bool,
    expand_outputs: bool,
) -> None:
    """Render all completed turns in the current conversation."""

    if not turns:
        return

    st.divider()
    st.markdown("## 当前对话")
    st.caption("这里会保留本窗口中的每一轮问题和 Agent 回答，方便继续追问。")
    render_conversation_export_button(turns, key="download_full_conversation")

    for index, turn in enumerate(turns, start=1):
        question = str(turn.get("question", ""))
        outputs = coerce_outputs(turn.get("outputs"))
        render_discussion_result(
            f"### 第 {index} 轮",
            question,
            outputs,
            show_process=show_process and index == len(turns),
            expand_outputs=expand_outputs,
            export_key=f"download_turn_{index}",
        )


def render_follow_up_form(
    turns: list[dict[str, object]],
    *,
    show_process: bool,
    expand_outputs: bool,
) -> bool:
    """Render a form for continuing the current conversation."""

    if not turns:
        return False

    st.divider()
    st.markdown("### 继续追问")
    st.caption("追问会自动带上本窗口前面几轮讨论作为上下文。")

    with st.form("follow_up_form", clear_on_submit=True):
        follow_up_question = st.text_area(
            label="继续在此谈话窗口提问",
            placeholder="例如：如果团队只有两个人，建议会有什么变化？",
            height=120,
        )
        submitted = st.form_submit_button("继续追问", type="primary")

    if not submitted:
        return False

    cleaned_question = follow_up_question.strip()
    if not cleaned_question:
        st.warning("请先输入追问内容。")
        return False

    st.markdown("## 本轮追问")
    with st.container(border=True):
        st.markdown(cleaned_question)

    contextual_question = build_follow_up_prompt(cleaned_question, turns)
    outputs = run_discussion(
        contextual_question,
        show_process=show_process,
        expand_outputs=expand_outputs,
    )
    save_discussion_turn(cleaned_question, outputs)
    return True


def render_sidebar_controls() -> tuple[bool, bool]:
    """Render sidebar options and return UI preferences."""

    with st.sidebar:
        settings = get_settings()
        st.header("显示设置")
        show_process = st.toggle("显示讨论过程", value=True)
        expand_outputs = st.toggle("默认展开 Agent 原文", value=True)

        if getattr(settings, "demo_mode", False):
            st.info("Demo 模式已启用：不会调用外部模型 API。")

        st.divider()
        st.markdown("#### 说明")
        st.caption(
            "讨论过程是面向用户的阶段记录、交叉回应和分析摘要，用于理解各 Agent 如何分工。"
            "它不是模型的隐藏思维链。"
        )

        st.divider()
        st.markdown("#### 调用顺序")
        for index, profile in enumerate(DISCUSSION_STAGES, start=1):
            st.markdown(f"{index}. **{profile.title}**：{profile.role}")

    return show_process, expand_outputs


def render_initial_question_form() -> tuple[bool, str]:
    """Render the first-turn question form and return submit state."""

    st.markdown("### 开始一次讨论")
    input_column, guide_column = st.columns([0.66, 0.34], gap="large")
    with input_column:
        with st.form("initial_question_form", clear_on_submit=False):
            question = st.text_area(
                label="请输入你的问题",
                placeholder="例如：我们是否应该把当前单体应用拆成微服务？",
                height=180,
            )
            submitted = st.form_submit_button("开始讨论", type="primary")

    with guide_column:
        with st.container(border=True):
            st.markdown("#### 本次流程")
            st.markdown(
                """
                1. GPT、Claude、Gemini 先各自给出首轮观点
                2. 三个 Agent 再依次回应彼此观点
                3. Critic 评审首轮观点和交叉回应
                4. Moderator 汇总为最终建议
                """
            )

    return submitted, question


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
        render_discussion_timeline(
            timeline_placeholder, outputs, active_keys={profile.key}
        )

    with st.spinner(profile.spinner):
        outputs[profile.key] = runner()

    progress_bar.progress(
        step_index / len(DISCUSSION_STAGES),
        text=f"已完成：{profile.title}",
    )

    if show_process:
        render_discussion_timeline(timeline_placeholder, outputs, active_keys=None)

    render_agent_output(profile, outputs[profile.key], expanded=expand_outputs)


def run_first_round(
    runners: dict[str, Callable[[], str]],
    outputs: dict[str, str],
    timeline_placeholder: st.delta_generator.DeltaGenerator,
    progress_bar: st.delta_generator.DeltaGenerator,
    *,
    show_process: bool,
    expand_outputs: bool,
) -> None:
    """Run the independent first-round agents concurrently, then render them.

    GPT / Claude / Gemini all answer the raw question with no dependency on one
    another, so they run in parallel threads (network-bound I/O). All Streamlit
    rendering stays on the main thread; the worker threads only call ``run``.
    The three cards therefore appear together once the batch finishes.
    """

    keys = list(runners)
    profiles = [get_profile(key) for key in keys]

    if show_process:
        render_discussion_timeline(timeline_placeholder, outputs, active_keys=set(keys))

    spinner_text = (
        " / ".join(profile.title for profile in profiles) + " 正在并行分析..."
    )
    with st.spinner(spinner_text):
        with ThreadPoolExecutor(max_workers=len(runners)) as executor:
            futures = {key: executor.submit(runner) for key, runner in runners.items()}
            for key, future in futures.items():
                outputs[key] = future.result()

    progress_bar.progress(
        len(runners) / len(DISCUSSION_STAGES),
        text=f"已完成首轮观点（{len(runners)} 个 Agent）",
    )

    if show_process:
        render_discussion_timeline(timeline_placeholder, outputs, active_keys=None)

    for profile in profiles:
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
    gpt_agent = OpenAIAgent()
    claude_agent = ClaudeAgent()
    gemini_agent = GeminiAgent()

    if show_process:
        render_discussion_timeline(timeline_placeholder, outputs, active_keys=None)

    run_first_round(
        {
            "GPT Agent": lambda: gpt_agent.run(question),
            "Claude Agent": lambda: claude_agent.run(question),
            "Gemini Agent": lambda: gemini_agent.run(question),
        },
        outputs,
        timeline_placeholder,
        progress_bar,
        show_process=show_process,
        expand_outputs=expand_outputs,
    )
    run_agent_step(
        get_profile("GPT Agent 交叉回应"),
        lambda: gpt_agent.run(
            build_peer_response_prompt(
                agent_name="GPT Agent",
                question=question,
                own_output=outputs["GPT Agent"],
                peer_outputs=get_peer_outputs(outputs, current_agent_key="GPT Agent"),
            )
        ),
        outputs,
        timeline_placeholder,
        progress_bar,
        4,
        show_process=show_process,
        expand_outputs=expand_outputs,
    )
    run_agent_step(
        get_profile("Claude Agent 交叉回应"),
        lambda: claude_agent.run(
            build_peer_response_prompt(
                agent_name="Claude Agent",
                question=question,
                own_output=outputs["Claude Agent"],
                peer_outputs=get_peer_outputs(
                    outputs,
                    current_agent_key="Claude Agent",
                ),
                prior_responses=get_cross_response_outputs(outputs),
            )
        ),
        outputs,
        timeline_placeholder,
        progress_bar,
        5,
        show_process=show_process,
        expand_outputs=expand_outputs,
    )
    run_agent_step(
        get_profile("Gemini Agent 交叉回应"),
        lambda: gemini_agent.run(
            build_peer_response_prompt(
                agent_name="Gemini Agent",
                question=question,
                own_output=outputs["Gemini Agent"],
                peer_outputs=get_peer_outputs(
                    outputs,
                    current_agent_key="Gemini Agent",
                ),
                prior_responses=get_cross_response_outputs(outputs),
            )
        ),
        outputs,
        timeline_placeholder,
        progress_bar,
        6,
        show_process=show_process,
        expand_outputs=expand_outputs,
    )
    run_agent_step(
        get_profile("Critic Agent"),
        lambda: CriticAgent().run(
            question=question,
            gpt_answer=answer_for_review(outputs, "GPT Agent"),
            claude_answer=answer_for_review(outputs, "Claude Agent"),
            gemini_answer=answer_for_review(outputs, "Gemini Agent"),
            peer_discussion=build_review_context(outputs),
        ),
        outputs,
        timeline_placeholder,
        progress_bar,
        7,
        show_process=show_process,
        expand_outputs=expand_outputs,
    )
    run_agent_step(
        get_profile("Moderator Agent"),
        lambda: ModeratorAgent().run(
            question=question,
            gpt_answer=answer_for_review(outputs, "GPT Agent"),
            claude_answer=answer_for_review(outputs, "Claude Agent"),
            gemini_answer=answer_for_review(outputs, "Gemini Agent"),
            critic_answer=answer_for_review(outputs, "Critic Agent"),
            peer_discussion=build_review_context(outputs),
        ),
        outputs,
        timeline_placeholder,
        progress_bar,
        8,
        show_process=show_process,
        expand_outputs=expand_outputs,
    )

    render_summary_panel(outputs)
    render_final_answer(outputs["Moderator Agent"])
    render_export_button(question, outputs, key="download_current_discussion")

    return outputs


def main() -> None:
    """Render the Streamlit app."""

    st.set_page_config(page_title="多 AI 讨论室", page_icon="🧠", layout="wide")
    initialize_session_state()
    show_process, expand_outputs = render_sidebar_controls()
    apply_page_styles()
    render_hero()
    render_agent_board()

    current_turn_started = False
    submitted, question = render_initial_question_form()
    if submitted:
        cleaned_question = question.strip()
        if not cleaned_question:
            st.warning("请先输入一个问题。")
            return

        outputs = run_discussion(
            cleaned_question,
            show_process=show_process,
            expand_outputs=expand_outputs,
        )
        save_discussion_turn(cleaned_question, outputs)
        current_turn_started = True

    turns = get_discussion_turns()
    if current_turn_started:
        render_follow_up_form(
            turns,
            show_process=show_process,
            expand_outputs=expand_outputs,
        )
    else:
        render_conversation_history(
            turns,
            show_process=show_process,
            expand_outputs=expand_outputs,
        )
        follow_up_submitted = render_follow_up_form(
            turns,
            show_process=show_process,
            expand_outputs=expand_outputs,
        )
        if follow_up_submitted:
            st.rerun()


if __name__ == "__main__":
    main()
