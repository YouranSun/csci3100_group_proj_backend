# prompt/split_commit_prompt.py

ATOMIC_SPLIT_SYSTEM_PROMPT = """\
You are a senior software engineer skilled in version control and code review.
Your task is to split a large commit into smaller, atomic commits.
Each atomic commit should represent a single logical change.
"""

def build_atomic_split_prompt(diff_summary: str) -> str:
    """构造用于建议 commit 拆分断点（start indices）的 prompt"""
    return f"""
{ATOMIC_SPLIT_SYSTEM_PROMPT}

Given the following diff summary, identify atomic split points.

IMPORTANT:
- You should return ONLY the START INDICES of each atomic commit.
- These indices refer to the 'new_lines' array of the file (0-based).
- The first split index MUST be 0.
- Indices MUST be strictly increasing.
- The final commit implicitly ends at the end of 'new_lines'.

These split points will be used as:
    start = split_points[i]
    end   = split_points[i + 1]

Only introduce split points when there is a clear logical boundary
(e.g., different functions, independent features, unrelated refactors).

Output STRICTLY in the following JSON format:

{{
  "splits": [
    {{
      "file": "<filename>",
      "split_lines": [0, 12, 27]
    }}
  ]
}}

Here is the diff summary:

{diff_summary}

Return ONLY the JSON. Do NOT include explanations or extra text.
"""
