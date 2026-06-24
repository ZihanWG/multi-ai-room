# 多 AI 讨论室 / Multi AI Discussion Room

[![CI](https://github.com/ZihanWG/multi-ai-room/actions/workflows/ci.yml/badge.svg)](https://github.com/ZihanWG/multi-ai-room/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

一个基于 Python 3.12 和 Streamlit 的本地多 Agent 讨论应用。用户输入问题后，系统会按顺序调用多个 AI Agent，让 GPT、Claude 和 Gemini 互相回应，再生成批判评审和最终建议。

A local multi-agent discussion app built with Python 3.12 and Streamlit. After the user enters a question, the app calls several AI agents in sequence, asks GPT, Claude, and Gemini to respond to each other, then produces critique and a final recommendation.

1. OpenAI GPT Agent：严谨分析、逻辑推理、识别隐含假设
   OpenAI GPT Agent: rigorous analysis, logical reasoning, and implicit-assumption detection.
2. Anthropic Claude Agent：结构化表达、风险提示、保守判断
   Anthropic Claude Agent: structured communication, risk notes, and conservative judgment.
3. Google Gemini Agent：发散思考、多方案比较、替代路径
   Google Gemini Agent: divergent thinking, option comparison, and alternative paths.
4. Critic Agent：批判前三个 Agent 的回答，指出漏洞和分歧
   Critic Agent: reviews the first three answers and highlights gaps and disagreements.
5. Moderator Agent：整合观点，输出最终结论和行动建议
   Moderator Agent: synthesizes all views into a final conclusion and action list.

## 功能说明 / Features

- 使用 Streamlit 提供本地 Web 聊天界面。
  Local web UI powered by Streamlit.
- 使用 `openai` SDK 调用 OpenAI 模型。
  Calls OpenAI models through the `openai` SDK.
- 使用 `anthropic` SDK 调用 Claude 模型。
  Calls Claude models through the `anthropic` SDK.
- 使用 `google-genai` SDK 调用 Gemini 模型。
  Calls Gemini models through the `google-genai` SDK.
- 使用 `python-dotenv` 从 `.env` 读取 API Key 和模型名。
  Loads API keys and model names from `.env` with `python-dotenv`.
- 每个 Agent 独立显示输出，Moderator Agent 的最终结论突出显示。
  Displays each agent output separately and highlights the Moderator final answer.
- GPT、Claude 和 Gemini 会先给首轮观点，再进行一轮可见的交叉回应。
  GPT, Claude, and Gemini first provide initial views, then produce a visible peer-response round.
- 单个模型调用失败不会导致整个应用崩溃。
  A single provider failure does not crash the whole app.
- API Key 缺失时会在对应 Agent 区域显示清晰错误信息。
  Missing API keys produce clear per-agent messages.
- 页面提供角色看板、讨论过程时间线、进度条和最终结论面板。
  Includes a role board, discussion timeline, progress indicator, and final summary panel.
- 支持 Demo 模式，不配置 API Key 也能体验完整流程。
  Includes Demo Mode so users can try the full flow without API keys.
- 支持将讨论结果导出为 Markdown。
  Supports exporting discussion results as Markdown.
- 支持在同一谈话窗口继续追问，并自动携带前几轮上下文。
  Supports follow-up questions in the same conversation window with prior context included automatically.
- 主题跟随 Streamlit 顶部菜单里的 Light/Dark/System：浅色模式保留默认浅色界面，深色模式启用项目暗色配色；侧边栏可以控制是否显示讨论过程、是否默认展开 Agent 原文。
  The theme follows Streamlit's built-in Light/Dark/System selector: light mode keeps the default light interface, while dark mode enables the app's dark palette; sidebar controls can show/hide the discussion process and expand/collapse raw agent outputs.
- 讨论过程展示的是面向用户的阶段记录和分析摘要，不是模型隐藏思维链。
  The discussion process shows user-facing notes and summaries, not hidden chain-of-thought.
- 支持用 Python 标准库 `unittest` 做基础测试。
  Uses Python standard-library `unittest` for basic tests.
- 提供 GitHub Actions CI 配置。
  Includes GitHub Actions CI.

## 项目结构 / Project Structure

```text
multi-ai-room/
├── app.py
├── styles.py
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── SECURITY.md
├── Makefile
├── .editorconfig
├── .python-version
├── .env.example
├── .gitattributes
├── .gitignore
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── config.yml
│   │   └── feature_request.yml
│   ├── pull_request_template.md
│   └── workflows/
│       └── ci.yml
├── docs/
│   └── ARCHITECTURE.md
├── agents/
│   ├── __init__.py
│   ├── base.py
│   ├── openai_agent.py
│   ├── claude_agent.py
│   ├── gemini_agent.py
│   ├── critic_agent.py
│   ├── moderator_agent.py
│   └── provider_calls.py
├── utils/
│   ├── __init__.py
│   ├── agent_errors.py
│   ├── conversation.py
│   ├── config.py
│   ├── demo.py
│   ├── discussion.py
│   ├── discussion_runner.py
│   ├── export.py
│   ├── prompts.py
│   └── roundtable.py
└── tests/
    ├── __init__.py
    ├── test_agent_errors.py
    ├── test_agents_missing_keys.py
    ├── test_conversation.py
    ├── test_config.py
    ├── test_demo.py
    ├── test_discussion.py
    ├── test_discussion_runner.py
    ├── test_export.py
    ├── test_provider_calls.py
    └── test_roundtable.py
```

## 安装步骤 / Installation

建议使用 Python 3.12。当前项目在 Python 3.12.10 下验证通过。

Python 3.12 is recommended. The project has been verified with Python 3.12.10.

```bash
cd multi-ai-room
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

也可以使用 Makefile。

You can also use the Makefile.

```bash
make install
```

如果本机没有 `python3.12` 命令，也可以使用系统默认 Python 3，但建议确认版本。

If `python3.12` is not available, use your system Python 3, but check the version first.

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 如何创建 `.env` / Creating `.env`

复制示例文件。

Copy the example file.

```bash
cp .env.example .env
```

然后编辑 `.env`，填入你的真实 API Key。

Then edit `.env` and fill in your real API keys.

```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

OPENAI_MODEL=gpt-5.5
CLAUDE_MODEL=claude-opus-4-8
GEMINI_MODEL=gemini-3.1-pro

REQUEST_TIMEOUT_SECONDS=60
PROVIDER_MAX_RETRIES=2
MAX_OUTPUT_TOKENS=1200
MAX_PROMPT_CONTEXT_CHARS=1800

CRITIC_PROVIDER=auto
MODERATOR_PROVIDER=auto

DEMO_MODE=false
```

可以只配置部分 API Key。未配置的模型会在对应 Agent 输出区域显示错误提示，不会让应用整体崩溃。

You may configure only some API keys. Missing providers show clear messages in their agent output blocks without crashing the app.

`REQUEST_TIMEOUT_SECONDS` 控制单次服务商请求超时；`PROVIDER_MAX_RETRIES` 控制服务商 SDK 层重试次数，设置为 `0` 可关闭重试；`MAX_OUTPUT_TOKENS` 控制单次模型调用最大输出；`MAX_PROMPT_CONTEXT_CHARS` 控制每个前置 Agent 输出被带入后续 prompt 的最大字符数，避免追问和交叉回应时上下文无限膨胀。

`REQUEST_TIMEOUT_SECONDS` controls the timeout for each provider request; `PROVIDER_MAX_RETRIES` controls SDK-level provider retries and can be set to `0` to disable retries; `MAX_OUTPUT_TOKENS` caps each model response; `MAX_PROMPT_CONTEXT_CHARS` limits how much prior agent output is copied into later prompts.

`CRITIC_PROVIDER` 和 `MODERATOR_PROVIDER` 可设置为 `auto`、`openai`、`anthropic` 或 `gemini`。默认 `auto` 会按 OpenAI -> Anthropic -> Gemini 的顺序选择已配置 API Key 的服务商；如果自动模式下前一个服务商调用失败，会尝试下一个可用服务商。

`CRITIC_PROVIDER` and `MODERATOR_PROVIDER` accept `auto`, `openai`, `anthropic`, or `gemini`. The default `auto` mode tries configured providers in OpenAI -> Anthropic -> Gemini order and falls back to the next available provider if a call fails.

## Demo 模式 / Demo Mode

如果你只是想体验完整界面和讨论流程，可以启用 Demo 模式：

If you only want to try the complete UI and discussion flow, enable Demo Mode:

```env
DEMO_MODE=true
```

Demo 模式会返回稳定的本地模拟内容，不调用 OpenAI、Anthropic 或 Gemini，也不会产生 API 费用。

Demo Mode returns deterministic local sample responses. It does not call OpenAI, Anthropic, or Gemini, and it does not incur API costs.

## 依赖版本 / Dependency Versions

`requirements.txt` 固定了直接依赖版本，方便本地和 CI 复现。

`requirements.txt` pins direct dependency versions for local and CI reproducibility.

- `streamlit`
- `openai`
- `anthropic`
- `google-genai`
- `python-dotenv`

## 如何运行 / Running

```bash
streamlit run app.py
```

或使用 Makefile。

Or use the Makefile.

```bash
make run
```

启动后，浏览器会打开本地地址，通常是：

After startup, the browser usually opens:

```text
http://localhost:8501
```

## 如何测试是否成功 / Manual Smoke Test

1. 启动应用后，页面标题应显示「多 AI 讨论室」。
   After startup, the page title should show "多 AI 讨论室".
2. 在文本框中输入一个问题，例如「我是否应该把当前单体应用拆成微服务？」。
   Enter a question, for example: "Should we split the current monolith into microservices?"
3. 点击「开始讨论」。
   Click "开始讨论".
4. 页面应依次显示讨论过程、GPT/Claude/Gemini 首轮观点、三段交叉回应、Critic Agent 和最终结论。
   The page should show the discussion process, GPT/Claude/Gemini initial views, three peer responses, Critic Agent, and final answer.
5. 如果没有配置某个 API Key，对应区域应显示类似「缺少 OPENAI_API_KEY，请在 .env 文件中配置。」的提示。
   If an API key is missing, the corresponding block should show a clear missing-key message.

## 开发与测试 / Development and Testing

提交改动前建议运行：

Before submitting changes, run:

```bash
python -m py_compile app.py agents/*.py utils/*.py tests/*.py
python -m unittest discover -s tests
```

也可以使用：

Or use:

```bash
make check
```

GitHub Actions 会在 `main` 分支 push 和 pull request 上执行同样的基础检查。

GitHub Actions runs the same basic checks on pushes to `main` and on pull requests.

## 架构说明 / Architecture

Agent 调用顺序、状态保存和外部服务边界见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the agent flow, state management, and external service boundaries.

## 界面说明 / UI Notes

- 顶部「讨论席位」展示每个 Agent 的职责和本轮目标。
  The top role board shows each agent's responsibility and goal.
- 「讨论过程」区域会随着调用进度更新，展示每个 Agent 的输入来源、阶段状态和输出摘要。
  The discussion process area updates with each step, showing inputs, state, and output summaries.
- 交叉回应阶段展示的是模型之间面向用户的可读回应，不是模型隐藏思维链。
  The peer-response stages show user-facing responses between models, not hidden chain-of-thought.
- 主题跟随 Streamlit 顶部菜单里的 Light/Dark/System；深色模式会启用项目自己的暗色配色，覆盖顶部栏、侧边栏、卡片、输入框和结果区。
  The theme follows Streamlit's built-in Light/Dark/System selector; dark mode enables the app's own dark palette for the top bar, sidebar, cards, input fields, and result sections.
- 每个 Agent 的完整原文可以默认展开，也可以在侧边栏切换为手动展开。
  Full agent outputs can be expanded by default or manually through sidebar controls.
- 底部「最终结论」会突出显示 Moderator Agent 的汇总结果。
  The final answer section highlights the Moderator synthesis.
- 讨论完成后可以点击「导出 Markdown」下载完整讨论记录。
  After a discussion finishes, click "导出 Markdown" to download the full discussion record.
- 继续追问后，页面会保留本窗口中的多轮问题和回答，并可导出整段对话。
  After follow-up questions, the page keeps all turns in the current window and can export the whole conversation.

## 隐私与费用说明 / Privacy and Cost

- 本项目是本地应用，但会根据你的 `.env` 配置调用 OpenAI、Anthropic 和 Google Gemini。
  This is a local app, but it calls OpenAI, Anthropic, and Google Gemini based on your `.env` configuration.
- 用户输入的问题和各 Agent 的中间回答会发送给对应模型服务商。
  User questions and intermediate agent outputs may be sent to the configured model providers.
- 不要输入不应发送给第三方模型服务的机密信息、个人敏感信息或受保护数据。
  Do not enter confidential, personal, or protected data that should not be sent to third-party model services.
- 模型调用可能产生 API 费用，费用由你配置的 API Key 所属账号承担。
  Model calls may incur API costs, charged to the accounts behind your configured API keys.
- 一次完整讨论会包含首轮观点、交叉回应、评审和汇总，因此会产生多次模型调用。
  A full discussion includes initial views, peer responses, critique, and synthesis, so it performs multiple model calls.
- `DEMO_MODE=true` 时不会调用外部模型服务。
  When `DEMO_MODE=true`, no external model service is called.
- `.env` 已被 `.gitignore` 忽略，请不要提交真实 API Key。
  `.env` is ignored by `.gitignore`; do not commit real API keys.

## 常见问题 / FAQ

### 1. 为什么某个 Agent 显示 API Key 缺失？ / Why does an agent report a missing API key?

说明 `.env` 中没有配置对应 Key，或者运行命令不在项目目录中。建议在 `multi-ai-room` 目录下运行：

It means the matching key is missing from `.env`, or the app was not started from the project directory. Run from `multi-ai-room`:

```bash
streamlit run app.py
```

### 2. 为什么模型调用失败？ / Why did a model call fail?

常见原因包括：

Common causes include:

- API Key 无效或额度不足。
  Invalid API key or insufficient quota.
- 模型名不可用。
  Unavailable model name.
- 网络连接失败。
  Network failure.
- 对应服务商接口暂时不可用。
  Temporary provider outage.

错误信息会直接显示在对应 Agent 区域中，方便定位。

The error is displayed in the corresponding agent block for easier debugging.

### 3. 可以只使用 OpenAI 吗？ / Can I use OpenAI only?

可以。只配置 `OPENAI_API_KEY` 时，GPT Agent、Critic Agent 和 Moderator Agent 可以工作；Claude Agent 和 Gemini Agent 会显示 API Key 缺失提示。

Yes. If only `OPENAI_API_KEY` is configured, GPT Agent, Critic Agent, and Moderator Agent can work; Claude Agent and Gemini Agent will show missing-key messages.

### 4. 模型名可以修改吗？ / Can I change model names?

可以。直接修改 `.env` 中的模型名：

Yes. Edit the model names in `.env`:

```env
OPENAI_MODEL=gpt-5.5
CLAUDE_MODEL=claude-opus-4-8
GEMINI_MODEL=gemini-3.1-pro
```

## 如何扩展新的 Agent / Adding a New Agent

1. 在 `agents/` 目录中新建一个文件，例如 `deepseek_agent.py`。
   Create a new file in `agents/`, for example `deepseek_agent.py`.
2. 继承 `BaseAgent`，实现 `run()` 方法。
   Inherit from `BaseAgent` and implement `run()`.
3. 在 `agents/__init__.py` 中导出新 Agent。
   Export the new agent in `agents/__init__.py`.
4. 在 `app.py` 中按需要实例化并调用新 Agent。
   Instantiate and call the new agent from `app.py`.
5. 如果需要新的 API Key 或模型名，在 `utils/config.py`、`.env.example` 和 README 中补充对应配置。
   If new API keys or model names are needed, update `utils/config.py`, `.env.example`, and README.

示例骨架：

Example skeleton:

```python
from agents.base import BaseAgent


class NewAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            name="New Agent",
            role_prompt="你是 New Agent，负责某个明确任务。输出语言为中文。",
        )

    def run(self, question: str) -> str:
        try:
            return "这里返回模型输出"
        except Exception as exc:
            return f"{self.name} 调用失败：{exc}"
```

## 安全注意事项 / Security Notes

不要把 `.env` 上传到 GitHub。`.gitignore` 已经包含 `.env`，但提交代码前仍建议检查：

Do not upload `.env` to GitHub. `.gitignore` already includes `.env`, but check before committing:

```bash
git status
```

只提交 `.env.example`，不要提交真实密钥。

Commit `.env.example` only. Do not commit real secrets.

## 参与贡献 / Contributing

贡献流程和本地开发建议见 [CONTRIBUTING.md](CONTRIBUTING.md)。

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution flow and local development guidance.

行为准则见 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for the code of conduct.

## 变更记录 / Changelog

项目变更记录见 [CHANGELOG.md](CHANGELOG.md)。

See [CHANGELOG.md](CHANGELOG.md) for project changes.

## 安全 / Security

安全报告方式和 API Key 注意事项见 [SECURITY.md](SECURITY.md)。

See [SECURITY.md](SECURITY.md) for security reporting and API key guidance.

## 许可证 / License

本项目使用 MIT License，详见 [LICENSE](LICENSE)。

This project is licensed under the MIT License. See [LICENSE](LICENSE).
