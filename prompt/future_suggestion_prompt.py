from typing import List, Tuple

def build_future_prompt(requirements: str, commit_history: list[str], code_summary: List[Tuple[str, str, str]]) -> str:
    """
    生成一个提示词，用于 LLM 根据代码摘要、提交历史与用户目标生成未来开发建议。
    """

    # 格式化 commit 历史（保留前若干条以防 prompt 太长）
    commit_section = "\n".join([f"- {msg}" for msg in commit_history[-20:]]) or "（无历史提交）"

    # 格式化代码摘要
    summary_section = "\n".join(
        [f"- [{t}] {p}: {s}" for (p, t, s) in code_summary if s]
    ) or "(Summary not generated yet)"

    return f"""
You are an experienced software architect and code reviewer.

Your task is to analyze this repository's evolution and current codebase, 
then generate **specific, actionable suggestions** for its next possible improvements.

---
### Project Goal
{requirements or "No explicit goal provided by the user."}

---
### Recent Commit History
{commit_section}

---
### Current Code Summary
{summary_section}

---
### Output Format (Very Important)
Return **only valid JSON** with the following structure:

[
  {{
    "title": "Short actionable title",
    "description": "Why or how this should be done, based on commit or summary context",
    "priority": "high" | "medium" | "low",
    "category": "feature" | "performance" | "documentation" | "refactor" | "testing" | "general"
  }},
  ...
]

Ensure:
- JSON is valid (no extra commentary, no markdown)
- 3–6 items
- `priority` roughly indicates impact or urgency
- Use lowercase category strings
"""
