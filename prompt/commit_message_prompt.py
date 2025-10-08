# prompts/commit_message_prompt.py

COMMIT_MESSAGE_SYSTEM_PROMPT = """\
You are a helpful assistant that writes concise and meaningful Git commit messages.
Use imperative mood (e.g., "Add", "Fix", "Refactor").
Be specific about what changed, but keep it short (no more than 5 words).
"""

def build_commit_prompt(diff_summary: str) -> str:
    """构造用于生成 commit message 的 prompt"""
    return f"""
{COMMIT_MESSAGE_SYSTEM_PROMPT}

Here is the diff summary:

{diff_summary}

Return only the commit message:
"""