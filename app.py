"""Streamlit frontend for the multi AI discussion room."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import streamlit as st
import streamlit.components.v1 as components

from agents import ClaudeAgent, CriticAgent, GeminiAgent, ModeratorAgent, OpenAIAgent
from utils.config import get_settings
from utils.conversation import build_follow_up_prompt, coerce_outputs
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

    if not st.session_state[SESSION_TURNS_KEY] and st.session_state[SESSION_OUTPUTS_KEY]:
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


def get_theme_marker() -> str:
    """Return the marker class for the active Streamlit theme."""

    try:
        theme_type = str(st.context.theme.get("type") or "").lower()
    except Exception:
        theme_type = ""

    if theme_type == "dark":
        return "multi-ai-room-dark-mode-marker"
    return "multi-ai-room-light-mode-marker"


def sync_streamlit_theme_class() -> None:
    """Mirror Streamlit's active frontend theme onto the app root."""

    components.html(
        """
        <script>
        (() => {
            const root = window.parent.document;

            const luminanceFromBackground = (backgroundColor) => {
                const channels = backgroundColor.match(/[\\d.]+/g);
                if (!channels || channels.length < 3) {
                    return 1;
                }

                const [red, green, blue] = channels.map(Number);
                return (0.2126 * red + 0.7152 * green + 0.0722 * blue) / 255;
            };

            const syncThemeClass = () => {
                const app = root.querySelector(".stApp");
                if (!app || !root.body) {
                    return;
                }

                const bodyBackground = root.defaultView.getComputedStyle(root.body).backgroundColor;
                const isDarkTheme = luminanceFromBackground(bodyBackground) < 0.5;

                app.classList.toggle("multi-ai-room-theme-dark", isDarkTheme);
                app.classList.toggle("multi-ai-room-theme-light", !isDarkTheme);
            };

            syncThemeClass();

            const observer = new MutationObserver(syncThemeClass);
            observer.observe(root.body, {
                attributes: true,
                childList: true,
                subtree: true,
                attributeFilter: ["class", "style", "data-theme"],
            });

            window.setInterval(syncThemeClass, 500);
        })();
        </script>
        """,
        height=0,
    )


def apply_page_styles() -> None:
    """Apply lightweight visual styling for the Streamlit app."""

    st.markdown(f'<div class="{get_theme_marker()}"></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(20, 184, 166, 0.12), transparent 34rem),
                linear-gradient(135deg, #f8fbfa 0%, #eef8f6 42%, #ffffff 100%);
            color: #0f172a;
        }

        [data-testid="stAppViewContainer"],
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4,
        [data-testid="stMarkdownContainer"] h5,
        [data-testid="stMarkdownContainer"] h6,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stWidgetLabel"] p,
        [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"],
        [data-testid="stCaptionContainer"] p,
        [data-testid="stExpander"] summary p {
            color: #0f172a;
        }

        textarea {
            color: #0f172a !important;
            background: #ffffff !important;
            caret-color: #0f766e !important;
            border-color: #cbd5e1 !important;
        }

        textarea::placeholder {
            color: #94a3b8 !important;
        }

        textarea:focus {
            border-color: #0f766e !important;
            box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.18) !important;
            outline: none !important;
        }

        [data-testid="stExpander"] {
            border: 1px solid #dbe7e4;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.92);
        }

        [data-testid="stExpander"] details,
        [data-testid="stExpander"] summary {
            background: #ffffff !important;
            color: #0f172a !important;
        }

        [data-testid="stExpander"] summary p,
        [data-testid="stExpander"] summary span,
        [data-testid="stExpander"] summary svg {
            color: #0f172a !important;
            fill: #0f172a !important;
        }

        [data-testid="stSidebar"] {
            background: #f7fbfa;
            border-right: 1px solid #dbe7e4;
        }

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            color: #334155;
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

        div[data-testid="stButton"] > button,
        div[data-testid="stFormSubmitButton"] > button,
        div[data-testid="stDownloadButton"] > button {
            border-radius: 999px;
            padding: 0.65rem 1.25rem;
            font-weight: 750;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) {
            background:
                radial-gradient(circle at top left, rgba(94, 234, 212, 0.20), transparent 34rem),
                radial-gradient(circle at 85% 4rem, rgba(56, 189, 248, 0.12), transparent 30rem),
                linear-gradient(135deg, #08110f 0%, #101715 48%, #171717 100%);
            color: #e5f2ef;
            color-scheme: dark;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stHeader"] {
            background: rgba(8, 17, 15, 0.86);
            backdrop-filter: blur(12px);
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stToolbar"],
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stToolbar"] *,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stHeader"] button,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stHeader"] svg {
            color: #e5f2ef !important;
            fill: #e5f2ef !important;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stAppViewContainer"],
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stMarkdownContainer"] h1,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stMarkdownContainer"] h2,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stMarkdownContainer"] h3,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stMarkdownContainer"] h4,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stMarkdownContainer"] h5,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stMarkdownContainer"] h6,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stMarkdownContainer"] p,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stMarkdownContainer"] li,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stWidgetLabel"] p,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stMetricLabel"],
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stMetricValue"],
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stCaptionContainer"] p,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stExpander"] summary p {
            color: #e5f2ef;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stCaptionContainer"] p,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .agent-objective,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .timeline-meta,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .timeline-state {
            color: #a9bfba;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) textarea {
            color: #e5f2ef !important;
            background: #0b1513 !important;
            caret-color: #5eead4 !important;
            border-color: #2f4740 !important;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) textarea::placeholder {
            color: #718882 !important;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) textarea:focus {
            border-color: #5eead4 !important;
            box-shadow: 0 0 0 3px rgba(94, 234, 212, 0.22) !important;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stSidebar"] {
            background: #0b1311;
            border-right: 1px solid #273a35;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h4,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
            color: #d7e8e4;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .hero {
            border-color: #2c443d;
            background: rgba(16, 25, 23, 0.92);
            box-shadow: 0 22px 60px rgba(0, 0, 0, 0.35);
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .hero-eyebrow {
            color: #5eead4;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .hero h1 {
            color: #f3fffc;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .hero p {
            color: #bdd0cc;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .agent-card,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .timeline-card,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .final-card {
            border-color: #2c403a;
            background: rgba(17, 27, 24, 0.94);
            box-shadow: 0 18px 36px rgba(0, 0, 0, 0.26);
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .agent-title,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .timeline-title {
            color: #f3fffc;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .agent-role {
            color: #5eead4;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .timeline-card {
            border-left-color: #39554d;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .timeline-card.is-active {
            border-left-color: #5eead4;
            background: rgba(20, 184, 166, 0.16);
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .timeline-card.is-done {
            border-left-color: #2dd4bf;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .timeline-index {
            color: #05201c;
            background: #5eead4;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .status-pill {
            background: rgba(45, 212, 191, 0.16);
            color: #99f6e4;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) .final-card {
            border-left-color: #38bdf8;
            background: rgba(14, 37, 47, 0.92);
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stExpander"] {
            border-color: #2c403a;
            background: rgba(17, 27, 24, 0.94);
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stExpander"] details,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stExpander"] summary {
            background: #111b18 !important;
            color: #e5f2ef !important;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stExpander"] summary p,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stExpander"] summary span,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) [data-testid="stExpander"] summary svg {
            color: #e5f2ef !important;
            fill: #e5f2ef !important;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) div[data-testid="stVerticalBlockBorderWrapper"],
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) div[data-testid="stMetric"] {
            border-color: #2c403a !important;
            background: rgba(17, 27, 24, 0.72);
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) div[data-testid="stButton"] > button,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) div[data-testid="stFormSubmitButton"] > button,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) div[data-testid="stDownloadButton"] > button {
            border-color: rgba(94, 234, 212, 0.42);
            background: linear-gradient(135deg, #0f766e 0%, #155e75 100%);
            color: #f3fffc;
        }

        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) div[data-testid="stButton"] > button:hover,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) div[data-testid="stFormSubmitButton"] > button:hover,
        :is(.stApp.multi-ai-room-theme-dark, .stApp:has(.multi-ai-room-dark-mode-marker):not(.multi-ai-room-theme-light)) div[data-testid="stDownloadButton"] > button:hover {
            border-color: #99f6e4;
            box-shadow: 0 0 0 3px rgba(94, 234, 212, 0.16);
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    sync_streamlit_theme_class()


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

        for profile in DISCUSSION_STAGES:
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

    done_count = sum(1 for profile in DISCUSSION_STAGES if profile.key in outputs)
    failed_count = sum("调用失败" in output or "缺少" in output for output in outputs.values())
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
        render_discussion_timeline(timeline_placeholder, outputs, active_key=None)

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


def get_peer_outputs(
    outputs: dict[str, str],
    *,
    current_agent_key: str,
) -> dict[str, str]:
    """Return first-round outputs from the other discussion agents."""

    return {
        agent_key: outputs[agent_key]
        for agent_key in ("GPT Agent", "Claude Agent", "Gemini Agent")
        if agent_key != current_agent_key and agent_key in outputs
    }


def get_cross_response_outputs(outputs: dict[str, str]) -> dict[str, str]:
    """Return the visible peer-response outputs generated so far."""

    return {
        agent_key: outputs[agent_key]
        for agent_key in (
            "GPT Agent 交叉回应",
            "Claude Agent 交叉回应",
            "Gemini Agent 交叉回应",
        )
        if agent_key in outputs
    }


def build_review_context(outputs: dict[str, str]) -> str:
    """Build a compact context block for critic and moderator stages."""

    response_outputs = get_cross_response_outputs(outputs)
    if not response_outputs:
        return ""

    sections = [
        f"### {agent_name}\n{content.strip() or '无输出。'}"
        for agent_name, content in response_outputs.items()
    ]
    return "## GPT / Claude / Gemini 交叉回应记录\n\n" + "\n\n".join(sections)


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
        step_index / len(DISCUSSION_STAGES),
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
    gpt_agent = OpenAIAgent()
    claude_agent = ClaudeAgent()
    gemini_agent = GeminiAgent()

    if show_process:
        render_discussion_timeline(timeline_placeholder, outputs, active_key=None)

    run_agent_step(
        get_profile("GPT Agent"),
        lambda: gpt_agent.run(question),
        outputs,
        timeline_placeholder,
        progress_bar,
        1,
        show_process=show_process,
        expand_outputs=expand_outputs,
    )
    run_agent_step(
        get_profile("Claude Agent"),
        lambda: claude_agent.run(question),
        outputs,
        timeline_placeholder,
        progress_bar,
        2,
        show_process=show_process,
        expand_outputs=expand_outputs,
    )
    run_agent_step(
        get_profile("Gemini Agent"),
        lambda: gemini_agent.run(question),
        outputs,
        timeline_placeholder,
        progress_bar,
        3,
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
            gpt_answer=outputs["GPT Agent"],
            claude_answer=outputs["Claude Agent"],
            gemini_answer=outputs["Gemini Agent"],
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
            gpt_answer=outputs["GPT Agent"],
            claude_answer=outputs["Claude Agent"],
            gemini_answer=outputs["Gemini Agent"],
            critic_answer=outputs["Critic Agent"],
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

    st.set_page_config(page_title="多 AI 讨论室", page_icon="AI", layout="wide")
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
