# 安全策略 / Security Policy

## 支持范围 / Scope

当前项目是本地运行的 Streamlit 示例应用。安全反馈主要覆盖：

This project is a local Streamlit sample app. Security feedback mainly covers:

- API Key 泄露风险。
  API key leakage risks.
- 依赖或配置导致的敏感信息暴露。
  Sensitive information exposure caused by dependencies or configuration.
- 可能导致用户输入被发送到非预期服务的问题。
  Issues that may send user input to unintended services.
- 远程调用错误处理中的敏感信息回显。
  Sensitive data appearing in remote-call error handling.

## 报告安全问题 / Reporting a Vulnerability

请不要在公开 issue 中粘贴真实 API Key、访问令牌、日志中的敏感内容或 `.env` 文件内容。

Do not paste real API keys, access tokens, sensitive logs, or `.env` contents in public issues.

如果发现安全问题，请通过 GitHub 私有安全报告功能提交；如果仓库暂未启用该功能，请先创建一个不包含敏感细节的 issue，说明需要私下沟通安全问题。

If you find a security issue, use GitHub private vulnerability reporting. If that is not enabled, open a minimal public issue without sensitive details and ask for a private reporting path.

## API Key 处理 / API Key Handling

- 真实密钥只应放在本地 `.env` 文件中。
  Real keys should only be stored in the local `.env` file.
- `.env` 已被 `.gitignore` 忽略。
  `.env` is ignored by `.gitignore`.
- `.env.example` 只能包含占位符。
  `.env.example` must contain placeholders only.
- 提交前建议运行 `git status`，确认没有密钥文件被跟踪。
  Run `git status` before committing to confirm no secret files are tracked.

## 第三方服务 / Third-Party Services

本项目会根据配置调用 OpenAI、Anthropic 和 Google Gemini。用户输入会发送到对应服务商。请不要输入不应发送给第三方模型服务的机密信息。

This project calls OpenAI, Anthropic, and Google Gemini based on configuration. User input is sent to the corresponding provider. Do not enter confidential information that should not be sent to third-party model services.
