"""Visual styling and theme syncing for the Streamlit app.

Extracted from ``app.py`` so the page-level CSS lives apart from the
orchestration and rendering logic. ``apply_page_styles`` is the only entry
point ``app.py`` needs to call.
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


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
