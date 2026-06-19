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

### Changed / 变更

- `requirements.txt` 固定直接依赖版本。
  Direct dependencies are pinned in `requirements.txt`.
- README 现在包含 Python 3.12 安装、隐私与费用说明、测试和贡献流程。
  README now documents Python 3.12 setup, privacy and cost considerations, tests, and contribution flow.
