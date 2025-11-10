from typing import List, Dict
from llm.base import LLMBase
from prompt.split_commit_prompt import build_atomic_split_prompt


# ========= Step 2: 让 LLM 给出拆分建议 ==========
def suggest_commit_splits(llm: LLMBase, diff_dicts: List[Dict]) -> Dict:
    """
    调用 LLM 生成拆分建议。
    输出形式如：
    {
        "splits": [
            {"file": "src/utils.py", "split_lines": [5, 10]},
            ...
        ]
    }
    """
    prompt = build_atomic_split_prompt(diff_dicts)
    raw_output = llm.generate(prompt)

    # 尝试解析 JSON
    import json
    try:
        result = json.loads(raw_output)
        if "splits" not in result:
            raise ValueError
        return result
    except Exception:
        # 如果解析失败，返回空结构
        return {"splits": []}


# ========= Step 3: 应用拆分建议 ==========
def apply_split_suggestions(diff_dicts: List[Dict], split_result: Dict) -> List[Dict]:
    """
    根据 LLM 输出的分割建议，把每个 diff 拆成更小的原子 diff。
    保证输出格式与输入相同。
    """
    new_diffs = []
    split_map = {s["file"]: sorted(set(s.get("split_lines", []))) for s in split_result.get("splits", [])}

    for d in diff_dicts:
        file = d["file"]
        old_lines = d.get("old_lines", [])
        new_lines = d.get("new_lines", [])
        old_start = d.get("old_start", 0)
        new_start = d.get("new_start", 0)

        # 无拆分建议 → 原样保留
        if file not in split_map or not split_map[file]:
            new_diffs.append(d)
            continue

        # 构造拆分点（前后补全首尾）
        splits = split_map[file]
        split_points = [0] + [min(len(new_lines), s) for s in splits if s < len(new_lines)] + [len(new_lines)]

        for i in range(len(split_points) - 1):
            start_idx = split_points[i]
            end_idx = split_points[i + 1]

            old_slice = old_lines[start_idx:end_idx]
            new_slice = new_lines[start_idx:end_idx]

            new_diff = {
                "file": file,
                "old_start": old_start + start_idx,
                "new_start": new_start + start_idx,
                "old_lines": old_slice,
                "new_lines": new_slice,
            }
            new_diffs.append(new_diff)

    return new_diffs


# ========= Step 4: 组合式接口 ==========
def generate_atomic_commits(llm: LLMBase, diff_dicts: List[Dict]) -> List[Dict]:
    """
    高层接口：自动调用 LLM → 获取拆分建议 → 应用拆分。
    """
    split_result = suggest_commit_splits(llm, diff_dicts)
    atomic_diffs = apply_split_suggestions(diff_dicts, split_result)
    return atomic_diffs
