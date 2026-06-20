# 变更记录 / Changelog

本文件记录项目中的重要变更。

All notable changes to this project are documented in this file.

格式参考 Keep a Changelog 的精神；项目开始发布 tag 后会使用语义化版本。

The format follows the spirit of Keep a Changelog, and this project will use semantic versioning once tagged releases begin.

## [Unreleased] / 未发布

### Added / 新增

- 增加带角色看板、讨论时间线、侧边栏控制和最终汇总面板的 Streamlit UI。
  Added a Streamlit UI with role board, discussion timeline, sidebar controls, and final summary panel.
- 增加 GPT、Claude、Gemini、Critic 和 Moderator 角色 Agent。
  Added GPT, Claude, Gemini, Critic, and Moderator agent roles.
- 增加 `st.session_state` 持久化，显示设置变化不会丢弃讨论结果。
  Added `st.session_state` persistence so display setting changes do not discard discussion results.
- 增加开源项目配套文件：许可证、贡献指南、安全策略、CI、测试、issue 模板和 PR 模板。
  Added open-source project files: license, contributing guide, security policy, CI, tests, issue templates, and PR template.
- 增加中英双语文档。
  Added bilingual Chinese and English documentation.
- 增加 Demo 模式，无需 API Key 即可体验完整讨论流程。
  Added Demo Mode so users can try the full discussion flow without API keys.
- 增加 Markdown 导出功能。
  Added Markdown export for discussion results.
- 增加同一窗口继续追问能力，并保留多轮对话历史。
  Added follow-up questions in the same window with multi-turn conversation history.
- 增加整段对话 Markdown 导出。
  Added full-conversation Markdown export.
- 增加 GPT、Claude 和 Gemini 的可见交叉回应阶段。
  Added visible peer-response stages for GPT, Claude, and Gemini.

### Changed / 变更

- `requirements.txt` 固定直接依赖版本。
  Direct dependencies are pinned in `requirements.txt`.
- README 现在包含 Python 3.12 安装、隐私与费用说明、测试和贡献流程。
  README now documents Python 3.12 setup, privacy and cost considerations, tests, and contribution flow.
- 改进输入框聚焦反馈，点击后会显示更明显的光标和边框状态。
  Improved textarea focus feedback with a clearer caret and focus border.
- 改进深色界面，增强顶部栏、侧边栏、卡片、输入框和结果区的暗色对比度。
  Improved the dark interface with stronger contrast for the top bar, sidebar, cards, inputs, and result sections.
- 修复在 Streamlit 顶部菜单切换到 Light 后仍显示深色界面的问题。
  Fixed the UI staying dark after switching to Light in Streamlit's top menu.
