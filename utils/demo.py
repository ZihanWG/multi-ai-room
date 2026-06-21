"""Deterministic demo responses for running the app without API keys."""

from __future__ import annotations

from utils.prompts import (
    CLAUDE_ANSWER_HEADER,
    CONTINUE_INSTRUCTION,
    CURRENT_IDENTITY_MARKER,
    FOLLOW_UP_QUESTION_MARKER,
    GEMINI_ANSWER_HEADER,
    GPT_ANSWER_HEADER,
    ORIGINAL_QUESTION_MARKER,
    PEER_RESPONSE_MARKER,
)


def extract_marked_section(
    text: str,
    marker: str,
    stop_markers: tuple[str, ...],
) -> str | None:
    """Extract one marked section from a generated prompt."""

    if marker not in text:
        return None

    section = text.split(marker, maxsplit=1)[1].strip()
    for stop_marker in stop_markers:
        if stop_marker in section:
            section = section.split(stop_marker, maxsplit=1)[0].strip()
    return section


def extract_display_question(question: str) -> str:
    """Extract the user-facing question from a contextual prompt."""

    follow_up = extract_marked_section(
        question,
        FOLLOW_UP_QUESTION_MARKER,
        (f"\n\n{CONTINUE_INSTRUCTION}",),
    )
    if follow_up is not None:
        return follow_up

    original_question = extract_marked_section(
        question,
        ORIGINAL_QUESTION_MARKER,
        (
            f"\n\n{CURRENT_IDENTITY_MARKER}",
            f"\n\n{GPT_ANSWER_HEADER}",
            f"\n\n{CLAUDE_ANSWER_HEADER}",
            f"\n\n{GEMINI_ANSWER_HEADER}",
        ),
    )
    if original_question is not None:
        return original_question

    return question.strip()


def is_peer_response_prompt(question: str) -> bool:
    """Return whether a prompt asks for a visible cross-agent response."""

    return PEER_RESPONSE_MARKER in question


def build_demo_peer_response(agent_name: str, cleaned_question: str) -> str:
    """Return deterministic demo content for a peer-response round."""

    responses = {
        "GPT Agent": f"""
**Demo 模式提示**：这是本地模拟的 GPT 交叉回应，未调用 OpenAI。

**我同意的部分**：
- Claude 对风险边界和表达结构的提醒是必要的。
- Gemini 提出的多路径比较能帮助避免只盯着单一方案。

**我需要修正的判断**：
- 首轮回答偏重“先定义指标”，但现在还应同时明确最小验证范围。
- 对问题「{cleaned_question}」来说，直接做完整方案仍然过早。

**给下一轮的建议**：把方案拆成“必须做、可以延后、明确不做”三类，再让 Critic 检查证据不足的地方。
""".strip(),
        "Claude Agent": f"""
**Demo 模式提示**：这是本地模拟的 Claude 交叉回应，未调用 Anthropic。

**回应 GPT**：
- GPT 强调指标和验证范围是合理的，但需要补充负责人、时间窗口和验收口径。

**回应 Gemini**：
- Gemini 的多路径比较有价值，不过应避免把资源分散到太多路线。

**结构化修正**：
1. 先确认不可接受风险。
2. 再定义两周内能完成的最小范围。
3. 最后决定哪些功能进入开源前必做清单。

**当前判断**：对「{cleaned_question}」，更稳妥的路径是低风险补齐基础体验，而不是扩大范围。
""".strip(),
        "Gemini Agent": f"""
**Demo 模式提示**：这是本地模拟的 Gemini 交叉回应，未调用 Google Gemini。

**回应 GPT**：
- GPT 的指标优先思路可以保留，但需要转成更具体的功能优先级。

**回应 Claude**：
- Claude 的保守边界能降低风险，不过也要避免因为过度保守导致产品缺少亮点。

**替代取舍**：
- 短期：先补齐输入反馈、讨论可见性、导出和错误提示。
- 中期：再考虑持久化、分享链接和模型配置面板。
- 暂缓：复杂权限、团队协作和生产级部署。

**当前建议**：围绕「{cleaned_question}」先做能直接提升体验和可信度的改动。
""".strip(),
    }

    return responses.get(
        agent_name,
        f"**Demo 模式提示**：{agent_name} 暂无专用交叉回应。问题：{cleaned_question}",
    )


def build_demo_response(
    agent_name: str,
    question: str,
    *,
    context: str = "",
) -> str:
    """Return a realistic, deterministic response for demo mode."""

    cleaned_question = extract_display_question(question) or "未提供问题"
    if is_peer_response_prompt(question):
        return build_demo_peer_response(agent_name, cleaned_question)

    context_note = ""
    if context.strip():
        context_note = "\n\n**已参考的前置内容**：Demo 模式会模拟读取前置 Agent 输出，但不会调用外部模型。"

    responses = {
        "GPT Agent": f"""
**Demo 模式提示**：这是本地模拟输出，未调用 OpenAI。

**一句话判断**：这个问题需要先明确目标、约束和风险，再决定执行路径。

**关键依据**：
- 原始问题是：{cleaned_question}
- 当前信息不足以做绝对判断，适合先做小范围验证。
- 决策应同时考虑收益、成本、复杂度和回滚能力。

**隐含假设**：
- 用户希望得到可执行建议，而不是只要观点。
- 当前团队有能力做一次低风险试点。

**主要风险**：
- 过早下结论可能导致实现成本失控。
- 如果缺少指标，后续很难判断方案是否成功。

**建议**：先定义成功指标和约束，再用最小可行方案验证。{context_note}
""".strip(),
        "Claude Agent": f"""
**Demo 模式提示**：这是本地模拟输出，未调用 Anthropic。

**结构化拆解**：
1. 目标：回答「{cleaned_question}」背后的真实决策需求。
2. 约束：时间、预算、团队能力、外部依赖和风险承受度。
3. 输出：需要形成明确建议和下一步行动。

**限制条件**：
- Demo 模式不会访问真实模型，因此内容只用于体验流程。
- 实际决策仍需要结合真实上下文、数据和利益相关方反馈。

**风险清单**：
- 信息不完整导致判断偏差。
- 多 Agent 输出可能重复，需要 Critic 和 Moderator 去重。
- 如果问题太宽泛，最终建议会偏通用。

**保守建议**：先缩小问题范围，列出不可接受风险，再进入执行。{context_note}
""".strip(),
        "Gemini Agent": f"""
**Demo 模式提示**：这是本地模拟输出，未调用 Google Gemini。

**可选路径**：
- 路径 A：保持现状，只做小改进。收益是风险低，代价是突破有限。
- 路径 B：做一次小规模试点。收益是能获得真实反馈，代价是需要额外协调。
- 路径 C：直接全面推进。收益是速度快，代价是失败成本最高。

**推荐取舍**：
- 如果不确定性高，优先选择路径 B。
- 如果风险极低且收益明确，可以考虑路径 C。
- 如果资源紧张，先用路径 A 稳住基础体验。

**补充视角**：问题「{cleaned_question}」可以拆成技术可行性、组织成本和用户价值三条线同时评估。{context_note}
""".strip(),
        "Critic Agent": f"""
**Demo 模式提示**：这是本地模拟输出，未调用 OpenAI。

**重复观点**：
- 前三轮都强调了需要先明确目标和约束。
- 都倾向于先试点，而不是直接全面推进。

**不严谨之处**：
- 目前缺少真实业务指标、成本估算和时间窗口。
- 如果原始问题涉及具体技术栈，还需要补充系统现状。

**缺少证据**：
- 没有用户数据、性能数据、预算或团队能力信息。

**值得保留的建议**：
- 先定义成功指标。
- 先做小范围验证。
- 明确不可接受风险和回滚方案。

**主要分歧**：不是方向上的分歧，而是推进力度不同：保守优化、试点验证、全面推进。{context_note}
""".strip(),
        "Moderator Agent": f"""
**Demo 模式提示**：这是本地模拟输出，未调用 OpenAI。

## 问题拆解

原始问题是：{cleaned_question}

这个问题需要同时回答三件事：目标是否明确、风险是否可控、下一步是否可执行。

## 各 Agent 观点摘要

- GPT Agent 强调先明确假设、指标和风险。
- Claude Agent 强调结构化拆解和保守推进。
- Gemini Agent 提供了保持现状、试点、全面推进三种路径。
- Critic Agent 指出当前缺少证据，建议避免过度自信。

## 最可靠判断

在信息不足时，最稳妥的选择是小范围试点，而不是直接全面推进。

## 最终建议

先定义成功指标和不可接受风险，再选择一个低成本试点验证方案。试点完成后，根据数据决定扩大、调整或停止。

## 下一步行动清单

1. 写下目标和衡量指标。
2. 列出约束、风险和回滚条件。
3. 选择一个最小试点范围。
4. 设定复盘时间点。
5. 根据结果决定是否扩大推进。{context_note}
""".strip(),
    }

    return responses.get(
        agent_name,
        f"**Demo 模式提示**：{agent_name} 暂无专用模拟输出。问题：{cleaned_question}",
    )
