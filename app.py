"""Streamlit frontend for the multi AI discussion room."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import streamlit as st

from styles import apply_page_styles
from utils.attachments import (
    STREAMLIT_UPLOAD_FILE_TYPES,
    AttachmentValidationError,
    PreparedAttachment,
    attachment_records_from_prepared,
    build_question_with_attachments,
    coerce_attachment_records,
    format_file_size,
    prepare_uploaded_files,
    upload_limits_summary,
)
from utils.config import get_settings
from utils.conversation import build_follow_up_prompt, coerce_outputs
from utils.discussion_runner import DiscussionEvent, run_discussion_flow
from utils.export import build_conversation_markdown, build_discussion_markdown


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


def save_discussion_turn(
    question: str,
    outputs: dict[str, str],
    *,
    attachments: Sequence[Mapping[str, object]] | None = None,
) -> None:
    """Persist one discussion turn in Streamlit session state."""

    stored_outputs = outputs.copy()
    stored_attachments = coerce_attachment_records(attachments or [])
    turn: dict[str, object] = {
        "question": question,
        "outputs": stored_outputs,
    }
    if stored_attachments:
        turn["attachments"] = stored_attachments

    st.session_state[SESSION_QUESTION_KEY] = question
    st.session_state[SESSION_OUTPUTS_KEY] = stored_outputs
    st.session_state[SESSION_TURNS_KEY].append(turn)


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


def render_prepared_attachments(
    attachments: Sequence[PreparedAttachment],
) -> None:
    """Render freshly uploaded attachments with image previews."""

    if not attachments:
        return

    st.markdown("**上传附件**")
    for attachment in attachments:
        with st.container(border=True):
            st.markdown(f"**{attachment.name}**")
            st.caption(
                f"{attachment.mime_type or '未知类型'} · "
                f"{format_file_size(attachment.size_bytes)}"
            )

            if attachment.is_image:
                st.image(
                    attachment.content,
                    caption=attachment.name,
                    use_container_width=True,
                )
            elif attachment.text_excerpt:
                with st.expander("查看文本摘录", expanded=False):
                    st.code(attachment.text_excerpt, language="text")
            else:
                st.caption("已记录文件信息，未提取文本内容。")


def render_attachment_records(
    attachment_records: Sequence[Mapping[str, object]] | object,
) -> None:
    """Render stored attachment metadata for completed turns."""

    records = coerce_attachment_records(attachment_records)
    if not records:
        return

    st.markdown("**上传附件**")
    for record in records:
        with st.container(border=True):
            st.markdown(f"**{record['name']}**")
            st.caption(
                f"{record['mime_type'] or '未知类型'} · "
                f"{format_file_size(record['size_bytes'])}"
            )

            excerpt = str(record.get("text_excerpt", "")).strip()
            if excerpt:
                with st.expander("查看文本摘录", expanded=False):
                    st.code(excerpt, language="text")


def render_turn_input(
    question: str,
    attachments: Sequence[PreparedAttachment],
) -> None:
    """Render the current submitted question and uploads before generation."""

    st.markdown("## 本轮输入")
    with st.container(border=True):
        st.markdown(question or "_未输入文字问题_")
        render_prepared_attachments(attachments)


def render_export_button(
    question: str,
    outputs: dict[str, str],
    *,
    key: str,
    attachments: Sequence[Mapping[str, object]] | None = None,
) -> None:
    """Render a Markdown download button for a discussion result."""

    if not outputs:
        return

    st.download_button(
        label="导出 Markdown",
        data=build_discussion_markdown(
            question,
            outputs,
            attachments=attachments,
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
    attachment_records: Sequence[Mapping[str, object]] | None = None,
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
        render_attachment_records(attachment_records or [])

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
    render_export_button(
        question,
        outputs,
        key=export_key,
        attachments=attachment_records,
    )


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
        attachment_records = coerce_attachment_records(turn.get("attachments"))
        render_discussion_result(
            f"### 第 {index} 轮",
            question,
            outputs,
            attachment_records=attachment_records,
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
        uploaded_files = st.file_uploader(
            label="上传文件或图片（可选）",
            type=STREAMLIT_UPLOAD_FILE_TYPES,
            accept_multiple_files=True,
            help=upload_limits_summary(),
            key="follow_up_uploads",
        )
        submitted = st.form_submit_button("继续追问", type="primary")

    if not submitted:
        return False

    try:
        attachments = prepare_uploaded_files(uploaded_files)
    except AttachmentValidationError as exc:
        for message in exc.messages:
            st.warning(message)
        return False
    cleaned_question = follow_up_question.strip()
    if not cleaned_question and not attachments:
        st.warning("请先输入追问内容或上传附件。")
        return False
    if not cleaned_question:
        cleaned_question = "请结合这次上传的附件继续分析。"

    render_turn_input(cleaned_question, attachments)

    settings = get_settings()
    contextual_question = build_follow_up_prompt(
        cleaned_question,
        turns,
        max_chars_per_agent=settings.max_prompt_context_chars,
        max_chars_per_attachment=settings.max_attachment_context_chars,
    )
    discussion_question = build_question_with_attachments(
        contextual_question,
        attachments,
    )
    attachment_records = attachment_records_from_prepared(attachments)
    outputs = run_discussion(
        discussion_question,
        attachments=attachments,
        display_question=cleaned_question,
        attachment_records=attachment_records,
        show_process=show_process,
        expand_outputs=expand_outputs,
    )
    save_discussion_turn(
        cleaned_question,
        outputs,
        attachments=attachment_records,
    )
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
        st.markdown("#### 运行边界")
        st.caption(
            f"每轮基础模型调用：{len(DISCUSSION_STAGES)} 次；"
            "auto fallback 失败重试时可能增加。"
        )
        st.caption(f"单次请求超时：{settings.request_timeout_seconds:g} 秒")
        st.caption(f"服务商重试次数：{settings.provider_max_retries}")
        st.caption(f"单次最大输出：{settings.max_output_tokens} tokens")
        st.caption(f"后续上下文上限：{settings.max_prompt_context_chars} 字符/Agent")
        st.caption(
            f"历史附件摘录上限：{settings.max_attachment_context_chars} 字符/附件"
        )
        st.caption(
            f"Critic provider：{settings.critic_provider}；"
            f"Moderator provider：{settings.moderator_provider}"
        )

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


def render_initial_question_form() -> tuple[bool, str, list[object]]:
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
            uploaded_files = st.file_uploader(
                label="上传文件或图片（可选）",
                type=STREAMLIT_UPLOAD_FILE_TYPES,
                accept_multiple_files=True,
                help=upload_limits_summary(),
                key="initial_uploads",
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

    return submitted, question, list(uploaded_files or [])


def run_discussion(
    question: str,
    *,
    attachments: Sequence[PreparedAttachment] | None = None,
    display_question: str | None = None,
    attachment_records: Sequence[Mapping[str, object]] | None = None,
    show_process: bool,
    expand_outputs: bool,
) -> dict[str, str]:
    """Run all agents and render progress events."""

    outputs: dict[str, str] = {}
    settings = get_settings()
    progress_bar = st.progress(0, text="准备开始讨论")
    timeline_placeholder = st.empty()

    if show_process:
        render_discussion_timeline(timeline_placeholder, outputs, active_keys=None)

    def handle_discussion_event(event: DiscussionEvent) -> None:
        outputs.clear()
        outputs.update(event.outputs)

        if event.kind == "active":
            if show_process:
                render_discussion_timeline(
                    timeline_placeholder,
                    outputs,
                    active_keys=set(event.active_keys),
                )
            return

        if event.kind != "completed":
            return

        completed_count = sum(
            1 for profile in DISCUSSION_STAGES if profile.key in outputs
        )
        if len(event.completed_keys) > 1:
            progress_text = f"已完成首轮观点（{len(event.completed_keys)} 个 Agent）"
        elif event.completed_keys:
            progress_text = f"已完成：{get_profile(event.completed_keys[0]).title}"
        else:
            progress_text = "已完成"

        progress_bar.progress(
            completed_count / len(DISCUSSION_STAGES),
            text=progress_text,
        )

        if show_process:
            render_discussion_timeline(
                timeline_placeholder,
                outputs,
                active_keys=None,
            )

        for stage_key in event.completed_keys:
            render_agent_output(
                get_profile(stage_key),
                outputs[stage_key],
                expanded=expand_outputs,
            )

    with st.spinner("多 AI 讨论正在进行..."):
        outputs = run_discussion_flow(
            question,
            max_context_chars=settings.max_prompt_context_chars,
            attachments=attachments,
            on_event=handle_discussion_event,
        )

    render_summary_panel(outputs)
    render_final_answer(outputs["Moderator Agent"])
    render_export_button(
        display_question or question,
        outputs,
        key="download_current_discussion",
        attachments=attachment_records,
    )

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
    submitted, question, uploaded_files = render_initial_question_form()
    if submitted:
        try:
            attachments = prepare_uploaded_files(uploaded_files)
        except AttachmentValidationError as exc:
            for message in exc.messages:
                st.warning(message)
            return
        cleaned_question = question.strip()
        if not cleaned_question and not attachments:
            st.warning("请先输入一个问题或上传附件。")
            return
        if not cleaned_question:
            cleaned_question = "请分析我上传的附件，指出重点、风险和下一步建议。"

        render_turn_input(cleaned_question, attachments)
        discussion_question = build_question_with_attachments(
            cleaned_question,
            attachments,
        )
        attachment_records = attachment_records_from_prepared(attachments)
        outputs = run_discussion(
            discussion_question,
            attachments=attachments,
            display_question=cleaned_question,
            attachment_records=attachment_records,
            show_process=show_process,
            expand_outputs=expand_outputs,
        )
        save_discussion_turn(
            cleaned_question,
            outputs,
            attachments=attachment_records,
        )
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
