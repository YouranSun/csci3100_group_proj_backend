from typing import List, Dict
from llm.base import LLMBase
from prompt.split_commit_prompt import build_atomic_split_prompt
from Repository.diff import AtomicDiff, Hunk
import hashlib, json


# ========= Step 2: 让 LLM 给出拆分建议 ==========
def suggest_commit_splits(llm: LLMBase, diffs: List[AtomicDiff]) -> Dict:
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
    print(diffs)
    results = {"splits": []}
    for d in diffs:
        prompt = build_atomic_split_prompt(d.to_dict())
        raw_output = llm.generate(prompt)

        print(prompt, raw_output)

        import json
        try:
            result = json.loads(raw_output)
            if "splits" not in result:
                raise ValueError
            results["splits"].extend(result["splits"])
        except Exception:
            pass
    print(results)
    return results


# ========= Step 3: 应用拆分建议 ==========
def apply_split_suggestions(diffs: List[AtomicDiff], split_result: Dict) -> List[AtomicDiff]:
    """
    根据 LLM 输出的分割建议，把每个 diff 拆成更小的原子 diff。
    保证输出格式与输入相同。
    """
    new_diffs = []
    split_map = {s["file"]: sorted(set(s.get("split_lines", []))) for s in split_result.get("splits", [])}

    for d in diffs:
        file_path = d.file_path
        is_new_file = d.is_new_file
        is_deleted_file = d.is_deleted_file
        old_lines = d.hunk.old_lines if d.hunk.old_lines else []
        new_lines = d.hunk.new_lines if d.hunk.new_lines else []
        old_start = d.hunk.old_start if d.hunk.old_start else []
        new_start = d.hunk.new_start if d.hunk.new_start else []

        if file_path not in split_map or not split_map[file_path]:
            new_diffs.append(d)
            continue

        splits = split_map[file_path]
        split_points = [0] + [min(len(new_lines), s) for s in splits if s < len(new_lines)] + [len(new_lines)]

        for i in range(len(split_points) - 1):
            start_idx = split_points[i]
            end_idx = split_points[i + 1]

            if start_idx == end_idx:
                continue

            old_slice = old_lines[start_idx:end_idx]
            new_slice = new_lines[start_idx:end_idx]

            new_diff = AtomicDiff(
                file_path=file_path,
                is_new_file=is_new_file,
                is_deleted_file=is_deleted_file,
                hunk=Hunk(
                    old_start=old_start,
                    new_start=new_start + start_idx,
                    old_lines=old_slice,
                    new_lines=new_slice,
                )
            )
            new_diffs.append(new_diff)

    return new_diffs


# ========= Step 4: 组合式接口 ==========
def generate_atomic_commits(llm: LLMBase, diffs: List[AtomicDiff]) -> List[AtomicDiff]:
    """
    高层接口：自动调用 LLM → 获取拆分建议 → 应用拆分。
    """
    split_result = suggest_commit_splits(llm, diffs)
    atomic_diffs = apply_split_suggestions(diffs, split_result)
    return atomic_diffs
