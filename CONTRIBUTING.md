# Contributing

感谢你对多 AI 讨论室感兴趣。这个项目当前保持轻量，贡献重点是让本地运行、Agent 编排和界面体验更稳定。

## 本地开发

建议使用 Python 3.12。

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

也可以使用：

```bash
make install
make run
```

`.env` 只放本地 API Key，不要提交到 Git。

## 测试

提交前请至少运行：

```bash
python -m py_compile app.py agents/*.py utils/*.py tests/*.py
python -m unittest discover -s tests
```

或直接运行：

```bash
make check
```

## 提交建议

- 保持改动聚焦，一个 PR 解决一个明确问题。
- 新增 Agent 时，请同步更新 `agents/__init__.py`、`.env.example` 和 `README.md`。
- 不要提交真实 API Key、`.env`、`.venv`、缓存目录或编辑器配置。
- 如果改动会触发真实模型调用，请在 PR 说明里写清楚成本和外部服务影响。
- 面向用户的功能变化请同步更新 `CHANGELOG.md`。

## Issue 和 PR

仓库提供 bug report、feature request 和 PR 模板。请尽量使用模板填写，尤其是复现步骤、Python 版本和是否配置了 API Key。

报告问题时，请尽量包含：

- Python 版本
- 操作系统
- 运行命令
- 报错信息或截图
- 是否配置了 OpenAI、Anthropic 或 Gemini API Key
