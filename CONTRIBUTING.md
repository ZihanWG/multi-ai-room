# 贡献指南 / Contributing

感谢你对多 AI 讨论室感兴趣。这个项目当前保持轻量，贡献重点是让本地运行、Agent 编排和界面体验更稳定。

Thanks for your interest in Multi AI Discussion Room. This project is intentionally lightweight; contributions should focus on reliable local setup, agent orchestration, and UI clarity.

## 本地开发 / Local Development

建议使用 Python 3.12。

Python 3.12 is recommended.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

也可以使用 Makefile。

You can also use the Makefile.

```bash
make install
make run
```

`.env` 只放本地 API Key，不要提交到 Git。

Use `.env` for local API keys only. Do not commit it.

## 测试 / Testing

提交前请至少运行：

Before submitting, run at least:

```bash
python -m py_compile app.py agents/*.py utils/*.py tests/*.py
python -m unittest discover -s tests
```

或直接运行：

Or run:

```bash
make check
```

## 提交建议 / Contribution Guidelines

- 保持改动聚焦，一个 PR 解决一个明确问题。
  Keep changes focused; one PR should solve one clear problem.
- 新增 Agent 时，请同步更新 `agents/__init__.py`、`.env.example` 和 `README.md`。
  When adding an agent, update `agents/__init__.py`, `.env.example`, and `README.md`.
- 不要提交真实 API Key、`.env`、`.venv`、缓存目录或编辑器配置。
  Do not commit real API keys, `.env`, `.venv`, cache directories, or editor-local files.
- 如果改动会触发真实模型调用，请在 PR 说明里写清楚成本和外部服务影响。
  If a change triggers real model calls, describe cost and external service impact in the PR.
- 面向用户的功能变化请同步更新 `CHANGELOG.md`。
  User-facing changes should update `CHANGELOG.md`.

## Issue 和 PR / Issues and Pull Requests

仓库提供 bug report、feature request 和 PR 模板。请尽量使用模板填写，尤其是复现步骤、Python 版本和是否配置了 API Key。

The repository provides bug report, feature request, and PR templates. Please use them when possible, especially for reproduction steps, Python version, and configured API providers.

报告问题时，请尽量包含：

When reporting a problem, include:

- Python 版本。
  Python version.
- 操作系统。
  Operating system.
- 运行命令。
  Command used to run the app.
- 报错信息或截图。
  Error message or screenshot.
- 是否配置了 OpenAI、Anthropic 或 Gemini API Key。
  Whether OpenAI, Anthropic, or Gemini API keys are configured.
