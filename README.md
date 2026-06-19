# 多 AI 讨论室

一个本地可运行的 Streamlit Web 应用。用户输入问题后，系统会按顺序调用多个 AI Agent：

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

## 项目结构

```text
multi-ai-room/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── agents/
│   ├── __init__.py
│   ├── base.py
│   ├── openai_agent.py
│   ├── claude_agent.py
│   ├── gemini_agent.py
│   ├── critic_agent.py
│   └── moderator_agent.py
└── utils/
    ├── __init__.py
    └── config.py
```

## 安装步骤

建议使用 Python 3.11 或更高版本。

```bash
cd multi-ai-room
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

如果本机没有 `python3.11` 命令，也可以使用：

```bash
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

## 如何运行

```bash
streamlit run app.py
```

启动后，浏览器会打开本地地址，通常是：

```text
http://localhost:8501
```

## 如何测试是否成功

1. 启动应用后，页面标题应显示「多 AI 讨论室」。
2. 在文本框中输入一个问题，例如「我是否应该把当前单体应用拆成微服务？」。
3. 点击「开始讨论」。
4. 页面应依次显示 GPT Agent、Claude Agent、Gemini Agent、Critic Agent 和最终结论。
5. 如果没有配置某个 API Key，对应区域应显示类似「缺少 OPENAI_API_KEY，请在 .env 文件中配置。」的提示。

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
