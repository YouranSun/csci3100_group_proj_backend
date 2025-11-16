# prompt/split_commit_prompt.py

ATOMIC_SPLIT_SYSTEM_PROMPT = """\
You are a senior software engineer skilled in version control and code review.
Your goal is to split a given large commit into smaller, *atomic commits*.
Each atomic commit should correspond to a single logical change or feature.
"""

def build_atomic_split_prompt(diff_summary: str) -> str:
    """构造用于建议 commit 拆分点的 prompt"""
    return f"""
{ATOMIC_SPLIT_SYSTEM_PROMPT}

Given the following diff summary, please suggest atomic split points.
Each diff block may contain multiple unrelated code changes.
You should identify where to split them into smaller commits.
The division is needed only when there's a clear cut on the implemented function.

Output JSON format strictly as:
{{
  "splits": [
    {{
      "file": "<filename>",
      "split_lines": [int, ...]
    }},
    ...
  ]
}}

The 'split_lines' indices refer to the 'new_lines' section of each file (0-based).

Here is the diff summary:

{diff_summary}

Return only the JSON result, without any explanations:
"""
