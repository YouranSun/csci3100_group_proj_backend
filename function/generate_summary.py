from pathlib import Path
from llm.base import LLMBase
from prompt.summary_prompt import build_directory_summary_prompt, build_file_summary_prompt
from db.summary_db import SummaryDB
import repository
from collections import defaultdict
from typing import List, Tuple, Dict, Any

def summarize_file(llm: LLMBase, file_path, repo_root):
    """读取文件内容并生成摘要，返回相对路径"""
    rel_path = Path(file_path).resolve().relative_to(repo_root)
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    prompt = build_file_summary_prompt(rel_path.name, content)
    summary = llm.generate(prompt)
    print(f"file: {file_path} summary: {summary}")
    return str(rel_path), summary

def summarize_directory(llm: LLMBase, dir_path, repo_root, db: SummaryDB):
    """递归生成目录摘要，边生成边保存"""
    summaries = []

    for entry in sorted(Path(dir_path).iterdir()):
        # 跳过隐藏文件和不需要的目录
        if entry.name.startswith(".") or entry.name in {"venv", "__pycache__"}:
            continue
        if entry.is_dir() and entry.name == ".git":
            continue

        if entry.is_file():
            rel_path, summary = summarize_file(llm, entry, repo_root)
            summaries.append((rel_path, "file", summary))
            db.save_node(rel_path, "file", summary)
        elif entry.is_dir():
            rel_path, summary = summarize_directory(llm, entry, repo_root, db)
            summaries.append((rel_path, "dir", summary))
            db.save_node(rel_path, "dir", summary)

    merged_text = "\n".join([s[2] for s in summaries])
    rel_path = Path(dir_path).resolve().relative_to(repo_root)
    prompt = build_directory_summary_prompt(rel_path.name, merged_text)
    dir_summary = llm.generate(prompt)
    return str(rel_path), dir_summary

def generate_repository_abstract(llm: LLMBase, repo: repository):
    repo_root = Path(repo.repo_path).resolve()
    db = SummaryDB(repo.repo_path)
    db.clear_all_nodes()

    # 根目录摘要，边递归边保存
    root_rel_path, root_summary = summarize_directory(llm, repo_root, repo_root, db)
    db.save_node(root_rel_path, "dir", root_summary)
    return root_summary

def print_summary_tree(db):
    """从 DB 输出树形摘要"""
    nodes_list = db.list_nodes()
    tree = lambda: defaultdict(tree)
    root = tree()
    summaries = {}

    # 构建树
    for rel_path, node_type, summary in nodes_list:
        parts = Path(rel_path).parts
        curr = root
        for part in parts:
            curr = curr[part]
        summaries[str(Path(rel_path))] = (node_type, summary)

    def _print(curr_tree, prefix="", parent_path="."):
        # 输出根节点
        if prefix == "":
            node_type, summary = summaries.get(parent_path, ("unknown", None))
            print(f". ({node_type})")
            if summary:
                for line in summary.splitlines():
                    print(f"    {line}")

        entries = sorted(curr_tree.keys())
        for i, name in enumerate(entries):
            connector = "└── " if i == len(entries) - 1 else "├── "
            full_path = str(Path(parent_path) / name)
            node_type, summary = summaries.get(full_path, ("unknown", None))
            print(f"{prefix}{connector}{name} ({node_type})")
            if summary:
                for line in summary.splitlines():
                    print(f"{prefix}    {line}")
            _print(curr_tree[name], prefix + ("    " if i == len(entries) - 1 else "│   "), full_path)

    _print(root)


# 工具：把平铺 nodes 转成树

from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Any, Tuple

from collections import defaultdict
from pathlib import Path
from typing import List, Tuple, Dict, Any

def build_tree(nodes: List[Tuple[str, str, str]]) -> List[Dict[str, Any]]:
    """
    nodes: list of (rel_path, node_type, summary)
    Return: a single root node '.' with children (same logic as print_summary_tree)
    """
    def tree():
        return defaultdict(tree)

    root = tree()
    summaries: Dict[str, Tuple[str, str]] = {}

    # Build nested dict and summary map
    for rel_path, node_type, summary in nodes:
        parts = Path(rel_path).parts or (".",)
        curr = root
        for part in parts:
            curr = curr[part]
        summaries[str(Path(rel_path))] = (node_type, summary)

    def build_children(curr_tree, parent_path: str) -> List[Dict[str, Any]]:
        result = []
        for name in sorted(curr_tree.keys()):
            # 跳过 '.' 自身，防止嵌套
            if parent_path == "." and name == ".":
                continue
            full_path = str(Path(parent_path) / name) if parent_path != "." else str(Path(name))
            node_type, summary = summaries.get(full_path, ("unknown", None))
            child_children = build_children(curr_tree[name], full_path)
            result.append({
                "name": name,
                "type": node_type,
                "summary": summary,
                "children": child_children
            })
        return result

    # Root node info
    root_type, root_summary = summaries.get(".", ("dir", None))
    root_children = build_children(root, ".")

    return [{
        "name": ".",
        "type": root_type,
        "summary": root_summary,
        "children": root_children
    }]