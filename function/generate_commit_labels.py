from llm.base import LLMBase
from prompt.label_commit_prompt import build_commit_category_prompt, CORE_CATEGORIES

def summarize_diff(diff_dicts):
    lines = []
    for d in diff_dicts:
        lines.append(f"File: {d['file_path']}")
        lines.append(f"Is New File: {d['is_new_file']}")
        lines.append(f"Is Deleted File: {d['is_deleted_file']}")
        if d['old_lines']:
            lines.append("Removed:")
            lines += [f"  - {x}" for x in d['old_lines']]
        if d['new_lines']:
            lines.append("Added:")
            lines += [f"  + {x}" for x in d['new_lines']]
        lines.append("")
    return "\n".join(lines)


def generate_labels(llm: LLMBase, messages: list[str]):
    results = []

    for idx, message in enumerate(messages):
        prompt = build_commit_category_prompt(message)
        raw = llm.generate(prompt).strip()

        try:
            label_idx = int(raw)
        except ValueError:
            label_idx = -1

        if 0 <= label_idx < len(CORE_CATEGORIES):
            category = CORE_CATEGORIES[label_idx]
        else:
            category = "unclear"

        results.append({
            "index": idx,
            "message": message,
            "category": category,
        })

    return results