# 多 AI 讨论室

[![CI](https://github.com/ZihanWG/multi-ai-room/actions/workflows/ci.yml/badge.svg)](https://github.com/ZihanWG/multi-ai-room/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

一个基于 Python 3.12 和 Streamlit 的本地多 Agent 讨论应用。用户输入问题后，系统会按顺序调用多个 AI Agent：

1. OpenAI GPT Agent：严谨分析、逻辑推理、识别隐含假设
2. Anthropic Claude Agent：结构化表达、风险提示、保守判断
3. Google Gemini Agent：发散思考、多方案比较、替代路径
4. Critic Agent：批判前三个 Agent 的回答，指出漏洞和分歧
5. Moderator Agent：整合观点，输出最终结论和行动建议

## 功能说明

- 使用 Streamlit 提供本地 Web 聊天界面
- 使用 `openai` SDK 调用 OpenAI 模型
- 使用 `anthropic` SDK 调用 Claude 模型
- 使用 `google-genai` SDK 调用 Gemini 模型
- 使用 `python-dotenv` 从 `.env` 读取 API Key 和模型名
- 每个 Agent 独立显示输出
- Moderator Agent 的最终结论突出显示
- 单个模型调用失败不会导致整个应用崩溃
- API Key 缺失时会在对应 Agent 区域显示清晰错误信息
- 页面提供角色看板、讨论过程时间线、进度条和最终结论面板
- 侧边栏可以控制是否显示讨论过程、是否默认展开 Agent 原文
- 讨论过程展示的是面向用户的阶段记录和分析摘要，不是模型隐藏思维链
- 支持用 Python 标准库 `unittest` 做基础测试
- 提供 GitHub Actions CI 配置

## 项目结构

```text
multi-ai-room/
├── app.py
├── requirements.txt
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
│   └── moderator_agent.py
├── utils/
│   ├── __init__.py
│   └── config.py
└── tests/
    ├── __init__.py
    ├── test_agents_missing_keys.py
    └── test_config.py
```

## 安装步骤

建议使用 Python 3.12。当前项目在 Python 3.12.10 下验证通过。

```bash
cd multi-ai-room
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

也可以使用 Makefile：

```bash
make install
```

如果本机没有 `python3.12` 命令，也可以使用系统默认 Python 3，但建议确认版本：

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 如何创建 .env

复制示例文件：

```bash
cp .env.example .env
```

然后编辑 `.env`，填入你的真实 API Key：

```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

OPENAI_MODEL=gpt-4.1
CLAUDE_MODEL=claude-3-5-sonnet-latest
GEMINI_MODEL=gemini-1.5-flash
```

可以只配置部分 API Key。未配置的模型会在对应 Agent 输出区域显示错误提示，不会让应用整体崩溃。

## 依赖版本

`requirements.txt` 固定了直接依赖版本，方便本地和 CI 复现：

- `streamlit`
- `openai`
- `anthropic`
- `google-genai`
- `python-dotenv`

## 如何运行

```bash
streamlit run app.py
```

或使用：

```bash
make run
```

启动后，浏览器会打开本地地址，通常是：

```text
http://localhost:8501
```

## 如何测试是否成功

1. 启动应用后，页面标题应显示「多 AI 讨论室」。
2. 在文本框中输入一个问题，例如「我是否应该把当前单体应用拆成微服务？」。
3. 点击「开始讨论」。
4. 页面应依次显示讨论过程、GPT Agent、Claude Agent、Gemini Agent、Critic Agent 和最终结论。
5. 如果没有配置某个 API Key，对应区域应显示类似「缺少 OPENAI_API_KEY，请在 .env 文件中配置。」的提示。

## 开发与测试

提交改动前建议运行：

```bash
python -m py_compile app.py agents/*.py utils/*.py tests/*.py
python -m unittest discover -s tests
```

也可以使用：

```bash
make check
```

GitHub Actions 会在 `main` 分支 push 和 pull request 上执行同样的基础检查。

## 架构说明

Agent 调用顺序、状态保存和外部服务边界见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。

## 界面说明

- 顶部「讨论席位」展示每个 Agent 的职责和本轮目标。
- 「讨论过程」区域会随着调用进度更新，展示每个 Agent 的输入来源、阶段状态和输出摘要。
- 每个 Agent 的完整原文可以默认展开，也可以在侧边栏切换为手动展开。
- 底部「最终结论」会突出显示 Moderator Agent 的汇总结果。

## 隐私与费用说明

- 本项目是本地应用，但会根据你的 `.env` 配置调用 OpenAI、Anthropic 和 Google Gemini。
- 用户输入的问题和各 Agent 的中间回答会发送给对应模型服务商。
- 不要输入不应发送给第三方模型服务的机密信息、个人敏感信息或受保护数据。
- 模型调用可能产生 API 费用，费用由你配置的 API Key 所属账号承担。
- `.env` 已被 `.gitignore` 忽略，请不要提交真实 API Key。

## 常见问题

### 1. 为什么某个 Agent 显示 API Key 缺失？

说明 `.env` 中没有配置对应 Key，或者运行命令不在项目目录中。建议在 `multi-ai-room` 目录下运行：

```bash
streamlit run app.py
```

### 2. 为什么模型调用失败？

常见原因包括：

- API Key 无效或额度不足
- 模型名不可用
- 网络连接失败
- 对应服务商接口暂时不可用

错误信息会直接显示在对应 Agent 区域中，方便定位。

### 3. 可以只使用 OpenAI 吗？

可以。只配置 `OPENAI_API_KEY` 时，GPT Agent、Critic Agent 和 Moderator Agent 可以工作；Claude Agent 和 Gemini Agent 会显示 API Key 缺失提示。

### 4. 模型名可以修改吗？

可以。直接修改 `.env` 中的模型名：

```env
OPENAI_MODEL=gpt-4.1
CLAUDE_MODEL=claude-3-5-sonnet-latest
GEMINI_MODEL=gemini-1.5-flash
```

## 如何扩展新的 Agent

1. 在 `agents/` 目录中新建一个文件，例如 `deepseek_agent.py`。
2. 继承 `BaseAgent`，实现 `run()` 方法。
3. 在 `agents/__init__.py` 中导出新 Agent。
4. 在 `app.py` 中按需要实例化并调用新 Agent。
5. 如果需要新的 API Key 或模型名，在 `utils/config.py`、`.env.example` 和 README 中补充对应配置。

示例骨架：

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

## 安全注意事项

不要把 `.env` 上传到 GitHub。`.gitignore` 已经包含 `.env`，但提交代码前仍建议检查：

```bash
git status
```

只提交 `.env.example`，不要提交真实密钥。

## 参与贡献

贡献流程和本地开发建议见 [CONTRIBUTING.md](CONTRIBUTING.md)。
行为准则见 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

## 变更记录

项目变更记录见 [CHANGELOG.md](CHANGELOG.md)。

## 安全

安全报告方式和 API Key 注意事项见 [SECURITY.md](SECURITY.md)。

## 许可证

本项目使用 MIT License，详见 [LICENSE](LICENSE)。
