from llm.base import LLMBase
from prompt.commit_message_prompt import build_commit_prompt

def summarize_diff(diff_dicts):
    """把diff字典转化为人类可读的摘要"""
    lines = []
    for d in diff_dicts:
        lines.append(f"File: {d['file']}")
        if d['old_lines']:
            lines.append("Removed:")
            lines += [f"  - {x}" for x in d['old_lines']]
        if d['new_lines']:
            lines.append("Added:")
            lines += [f"  + {x}" for x in d['new_lines']]
        lines.append("")
    return "\n".join(lines)

def generate_commit_message(llm: LLMBase, diff_dicts):
    """调用 LLM 生成 commit message"""
    diff_summary = summarize_diff(diff_dicts)
    prompt = build_commit_prompt(diff_summary)
    return llm.generate(prompt)
