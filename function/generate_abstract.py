from pathlib import Path
from llm.base import LLMBase
from prompt.abstract_prompt import build_directory_abstract_prompt, build_file_abstract_prompt
from db.abstract_db import AbstractDB
import Repository
from collections import defaultdict

def summarize_file(llm: LLMBase, file_path, repo_root):
    """读取文件内容并生成摘要，返回相对路径"""
    rel_path = Path(file_path).resolve().relative_to(repo_root)
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    prompt = build_file_abstract_prompt(rel_path.name, content)
    summary = llm.generate(prompt)
    return str(rel_path), summary

def summarize_directory(llm: LLMBase, dir_path, repo_root, db: AbstractDB):
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
    prompt = build_directory_abstract_prompt(rel_path.name, merged_text)
    dir_summary = llm.generate(prompt)
    return str(rel_path), dir_summary

def generate_repository_abstract(llm: LLMBase, repo: Repository):
    repo_root = Path(repo.repo_path).resolve()
    db = AbstractDB(repo.repo_path)

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