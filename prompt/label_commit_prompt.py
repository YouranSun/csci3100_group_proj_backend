CORE_CATEGORIES = ["feat", "fix", "refactor", "docs", "chore"]

COMMIT_CATEGORY_SYSTEM_PROMPT = """\
You are an expert in classifying Git commits.

Your task is to assign a category INDEX based on the PRIMARY intent of the change.

Category indices:
0 = feat      (new or expanded behavior)
1 = fix       (bug fix or incorrect behavior)
2 = refactor  (code restructuring, no behavior change)
3 = docs      (documentation or comments only)
4 = chore     (other maintenance or engineering changes)

Rules:
- Return EXACTLY ONE integer from 0 to 4.
- Return -1 if the category is unclear.
- Do NOT explain your reasoning.
- Do NOT guess if unsure.
"""

def build_commit_category_prompt(diff_summary: str) -> str:
    return f"""
{COMMIT_CATEGORY_SYSTEM_PROMPT}

Here is the diff summary:

{diff_summary}

Return ONLY the category index (or -1 if unclear):
"""
