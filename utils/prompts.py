"""Shared prompt markers.

These literals are the single source of truth for the markers that appear in
generated prompts. The prompt builders (`utils.conversation`, `utils.roundtable`)
and the demo parser (`utils.demo`) all import them, so the demo's prompt
extraction stays in sync whenever a template changes.
"""

from __future__ import annotations

# Round labels and section headers used inside generated prompts.
PEER_RESPONSE_MARKER = "交叉回应任务"
ORIGINAL_QUESTION_MARKER = "用户原始问题："
FOLLOW_UP_QUESTION_MARKER = "用户新的追问："
CURRENT_IDENTITY_MARKER = "你当前身份："
CONTINUE_INSTRUCTION = "请继续按当前 Agent 角色完成本轮回答。"

# Per-agent answer headers used by the Critic and Moderator prompts.
GPT_ANSWER_HEADER = "GPT Agent 回答："
CLAUDE_ANSWER_HEADER = "Claude Agent 回答："
GEMINI_ANSWER_HEADER = "Gemini Agent 回答："
