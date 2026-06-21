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
- 增加 `ruff` 和 `mypy` 静态检查（lint 与类型检查），并接入 CI、`Makefile` 和 `requirements-dev.txt`。
  Added `ruff` and `mypy` static checks (lint and type-check) wired into CI, the `Makefile`, and `requirements-dev.txt`.

### Changed / 变更

- GPT、Claude、Gemini 的首轮观点改为并行生成，缩短首轮等待时间（三张卡片会一起出现）。
  The GPT, Claude, and Gemini first-round views are now generated in parallel, shortening first-round latency (the three cards appear together).
- Agent 调用失败或缺少 Key 的输出不再作为内容传入后续 Agent 的提示词。
  Failed or missing-key agent outputs are no longer passed into later agents' prompts as content.
- 共享提示词标记集中到 `utils/prompts.py`；拆分 `app.py`，样式移至 `styles.py`、讨论上下文助手移至 `utils/discussion.py`。
  Shared prompt markers are centralized in `utils/prompts.py`; `app.py` is split, with styles moved to `styles.py` and discussion context helpers to `utils/discussion.py`.

### Fixed / 修复

- 更新过时的默认模型为 `claude-opus-4-8` / `gpt-5.5` / `gemini-3.1-pro`，修复默认 Claude 模型已下线导致 Claude Agent 调用失败的问题。
  Updated stale default models to `claude-opus-4-8` / `gpt-5.5` / `gemini-3.1-pro`, fixing Claude Agent failures caused by the retired default Claude model.

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
