# 架构 / Architecture

这个项目刻意保持小而清晰。应用主要分为四层：

This project is intentionally small and clear. The app has four main layers:

1. `app.py` 中的 Streamlit UI。
   Streamlit UI in `app.py`.
2. `utils/discussion_runner.py` 中的讨论编排。
   Discussion orchestration in `utils/discussion_runner.py`.
3. `agents/` 中的 Agent 实现。
   Agent implementations in `agents/`.
4. `utils/config.py` 和其他 `utils/` 模块中的配置与纯函数 helper。
   Configuration and pure helper functions in `utils/config.py` and other `utils/` modules.

## 请求流程 / Request Flow

```mermaid
flowchart TD
    User["用户输入问题和可选附件 / User enters a question and optional uploads"] --> UI["Streamlit app.py"]
    UI --> Attachments["utils/attachments.py"]
    Attachments --> UI
    UI --> Runner["utils/discussion_runner.py"]
    Runner --> GPT["OpenAIAgent"]
    Runner --> Claude["ClaudeAgent"]
    Runner --> Gemini["GeminiAgent"]
    GPT --> GPTRound["GPT 交叉回应 / GPT peer response"]
    Claude --> GPTRound
    Gemini --> GPTRound
    GPT --> ClaudeRound["Claude 交叉回应 / Claude peer response"]
    Claude --> ClaudeRound
    Gemini --> ClaudeRound
    GPTRound --> ClaudeRound
    GPT --> GeminiRound["Gemini 交叉回应 / Gemini peer response"]
    Claude --> GeminiRound
    Gemini --> GeminiRound
    GPTRound --> GeminiRound
    ClaudeRound --> GeminiRound
    GPT --> Critic["CriticAgent"]
    Claude --> Critic
    Gemini --> Critic
    GPTRound --> Critic
    ClaudeRound --> Critic
    GeminiRound --> Critic
    GPT --> Moderator["ModeratorAgent"]
    Claude --> Moderator
    Gemini --> Moderator
    GPTRound --> Moderator
    ClaudeRound --> Moderator
    GeminiRound --> Moderator
    Critic --> Moderator
    Moderator --> Result["最终回答 / Final answer"]
    Result --> UI
```

## Agent 职责 / Agent Responsibilities

- `OpenAIAgent`：严谨分析、隐含假设识别和第一版判断。
  `OpenAIAgent`: rigorous analysis, implicit assumptions, and first-pass judgment.
- `ClaudeAgent`：结构、可读性、风险提示和保守判断。
  `ClaudeAgent`: structure, readability, risk notes, and conservative judgment.
- `GeminiAgent`：替代路径和方案比较。
  `GeminiAgent`: alternative paths and option comparison.
- GPT、Claude 和 Gemini 在首轮观点之后会各自生成一轮交叉回应，用于回应彼此的观点和修正判断。
  After the first-pass views, GPT, Claude, and Gemini each generate one peer-response round to respond to each other and revise their judgments.
- `CriticAgent`：批判 GPT、Claude 和 Gemini 的输出。
  `CriticAgent`: critique of GPT, Claude, and Gemini outputs.
- `ModeratorAgent`：最终综合和可执行建议。
  `ModeratorAgent`: final synthesis and actionable recommendations.

## 状态管理 / State Management

Streamlit 会在 UI 控件变化时重新运行应用。应用把最近一次完成的讨论存入 `st.session_state`，所以切换显示设置不会丢弃已有 Agent 输出，也不会再次触发模型调用。

Streamlit reruns the app whenever UI controls change. The app stores the last completed discussion in `st.session_state`, so toggling display settings does not discard previous agent output or trigger model calls again.

保存的值包括：

The saved values are:

- `discussion_question`
- `discussion_outputs`
- `discussion_turns`
- 每轮可选的 `attachments` 元数据和文本摘录
  Optional per-turn `attachments` metadata and text excerpts

`discussion_turns` 保存同一窗口中的多轮问题和 Agent 输出。追问时，`utils/conversation.py` 会把最近几轮讨论转换为上下文提示词，再交给当前 Agent 流程。

`discussion_turns` stores multiple questions and agent outputs in the same window. For follow-up questions, `utils/conversation.py` converts recent turns into a contextual prompt before passing it into the current agent flow.

上传附件由 `utils/attachments.py` 预处理。该模块会先限制文件数量、单文件大小、图片大小和总大小，并拒绝 `.env`、私钥、凭据等疑似敏感文件。文本、Markdown、CSV、JSON 和常见代码文件会被解码并截断为 prompt 摘录；常见图片会先通过文件签名校验，校验通过后在 UI 中预览，并按 provider-specific allowlist 作为多模态内容传给 GPT、Claude 和 Gemini 的首轮调用。附件内容会在 prompt 中标记为不可信用户资料，不会被当作系统或开发者指令。追问时，历史附件摘录会按 `MAX_ATTACHMENT_CONTEXT_CHARS` 再次截断，避免多轮附件上下文无限膨胀。后续交叉回应、Critic 和 Moderator 主要读取首轮输出和文本上下文。

Uploads are preprocessed by `utils/attachments.py`. The module first enforces file-count, per-file, image-size, and total-size limits, and rejects likely sensitive files such as `.env`, private keys, and credentials. Text, Markdown, CSV, JSON, and common code files are decoded and truncated into prompt excerpts; common images are validated by file signature, previewed in the UI when valid, and sent to GPT, Claude, and Gemini first-round calls according to provider-specific allowlists. Attachment contents are marked in prompts as untrusted user material, not as system or developer instructions. In follow-up prompts, historical attachment excerpts are truncated again with `MAX_ATTACHMENT_CONTEXT_CHARS` so multi-turn attachment context cannot grow without bound. Later peer-response, Critic, and Moderator stages primarily consume first-round outputs and textual context.

## 外部服务 / External Services

应用可以调用三个外部服务商：

The app can call three external providers:

- 通过 `openai` SDK 调用 OpenAI。
  OpenAI through the `openai` SDK.
- 通过 `anthropic` SDK 调用 Anthropic。
  Anthropic through the `anthropic` SDK.
- 通过 `google-genai` SDK 调用 Google Gemini。
  Google Gemini through the `google-genai` SDK.

API Key 由 `utils/config.py` 从 `.env` 加载。缺少 Key 是允许的：每个 Agent 会返回清晰的缺失 Key 提示，而不是让整个应用崩溃。

API keys are loaded from `.env` by `utils/config.py`. Missing keys are allowed: each agent returns a clear missing-key message instead of crashing the whole app.

如果 `DEMO_MODE=true`，Agent 会返回 `utils/demo.py` 中的本地模拟内容，不会调用外部服务。

If `DEMO_MODE=true`, agents return local deterministic sample responses from `utils/demo.py` and do not call external services.

`CriticAgent` 和 `ModeratorAgent` 默认使用 `auto` provider 选择：按 OpenAI、Anthropic、Gemini 的顺序选择已配置 API Key 的服务商，并在自动模式下尝试下一个可用服务商作为 fallback。也可以通过 `CRITIC_PROVIDER` 和 `MODERATOR_PROVIDER` 显式指定 `openai`、`anthropic` 或 `gemini`。

`CriticAgent` and `ModeratorAgent` default to `auto` provider selection: they try configured providers in OpenAI, Anthropic, Gemini order and fall back to the next available provider in automatic mode. `CRITIC_PROVIDER` and `MODERATOR_PROVIDER` can explicitly select `openai`, `anthropic`, or `gemini`.

## 导出 / Export

单轮讨论和整段对话都可以通过 `utils/export.py` 转换为 Markdown。Streamlit UI 使用同一个工具函数提供下载按钮，因此导出逻辑可以独立测试。

Single-turn discussions and full conversations can be converted to Markdown through `utils/export.py`. The Streamlit UI uses the same helper to provide download buttons, so export behavior can be tested independently.

导出内容包含附件元数据和文本摘录，但不包含原始二进制文件内容。

Exports include attachment metadata and text excerpts, but not raw binary file contents.

## 非目标 / Non-Goals

- 本项目不展示模型隐藏思维链；UI 只展示面向用户的摘要和讨论记录。
  This project does not expose model hidden chain-of-thought; the UI shows user-facing summaries and discussion records only.
- 本项目不会在本地环境之外代理或存储 API Key。
  This project does not proxy or store API keys outside the local environment.
- 本项目不提供生产级认证、限流、持久化或部署加固。
  This project does not provide production authentication, rate limiting, persistence, or deployment hardening.
