import re
import subprocess
import os
from pathlib import Path
from typing import List, Any, Dict
import hashlib
import json
import uuid
from collections import defaultdict

from git import Repo
from Repository.diff import AtomicDiff

from db.summary_db import SummaryDB
from db.commits_db import CommitsDB

from llm.base import LLMBase

from function.generate_summary import generate_repository_summary, build_tree
from function.apply_commit_groups import parse_diff_blocks, adjust_later_groups, adjust_later_diffs
from function.generate_future_suggestion import generate_future_suggestion
from function.generate_atomic_commits import generate_atomic_commits
from function.generate_suggested_commit_groups import generate_suggested_commit_groups_agglomerative
from function.generate_commit_message import generate_commit_message
from function.generate_commit_labels import generate_labels

ENV = {
    "GIT_AUTHOR_NAME": "LLM Commit Bot",
    "GIT_AUTHOR_EMAIL": "bot@example.com",
    "GIT_COMMITTER_NAME": "LLM Commit Bot",
    "GIT_COMMITTER_EMAIL": "bot@example.com",
}

class Repository:

    def __init__(self, path="."):
        print(path)
        self.repo_path = Path(path).resolve()
        try:
            self.repo = Repo(self.repo_path)
        except Exception as e:
            raise RuntimeError(f"Cannot open Git repo from {self.repo_path}: {e}")

    #----------#
    #    DB    #
    #----------#

    def get_summary_db(self) -> SummaryDB:
        return SummaryDB(self.repo_path)

    def get_commits_db(self) -> CommitsDB:
        return CommitsDB(self.repo_path)


    def to_dict(self):
        return {
            "path": str(self.repo_path),
            "name": getattr(self, "name", None) or self.repo_path.name,
            "last_commit": self.repo.head.commit.hexsha if self.repo.head else None
        }

    #-------------------------------#
    #    Git and file operations    #
    #-------------------------------#

    def apply_diff_group(self, group: dict, diffs: dict[str, AtomicDiff]):
        files = []
        for (i, diff_id) in enumerate(group["diff_ids"]):
            atomic = diffs[diff_id]
            atomic.apply(self.repo_path)
            files.append(self.repo_path / atomic.file_path)
            adjust_later_diffs(group, diffs, i)
        return files

    def stage_files(self, files: list[str]):
        subprocess.run(
            ["git", "add"] + files,
            cwd=self.repo_path,
            env={**os.environ, **ENV},
            check=True,
        )

    def commit(self, message: str):
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=self.repo_path,
            env={**os.environ, **ENV},
            check=True,
        )

    def reset_to_head(self):
        print(self.repo_path)
        subprocess.run(
            ["git", "reset", "--hard", "HEAD"],
            cwd=self.repo_path,
            env={**os.environ, **ENV},
            check=True,
        )
        subprocess.run(
            ["git", "clean", "-fd"],
            cwd=self.repo_path,
            env={**os.environ, **ENV},
            check=True,
        )


    def apply_commit_groups(self):
        groups = self.list_commit_groups()
        diffs = self.get_atomic_diffs()
        commit_messages = {}
        for group in groups:
            commit_messages[group["id"]] = self.get_commit_message(group["id"])
        applied = []

        self.reset_to_head()

        for i, group in enumerate(groups):
            gid = group["id"]
            msg = commit_messages.get(gid, f"Commit group {gid}")
            if msg is None:
                continue

            files = self.apply_diff_group(group, diffs)
            self.stage_files(files)
            print("commit message", msg)
            self.commit(msg)

            adjust_later_groups(groups, diffs, i)

            applied.append({
                "group_id": gid,
                "message": msg,
                "num_diffs": len(group["diff_ids"])
            })

        return applied

    def diff_with_head(self):
        diff_text = self.repo.git.diff("--cached", "--unified=0")
        return parse_diff_blocks(diff_text)

    def get_historical_commit_messages(self, limit=50):
        commits = list(self.repo.iter_commits("HEAD", max_count=limit))
        return [c.message.strip() for c in commits]

    #---------------#
    #    Summary    #
    #---------------#

    def generate_summary(self, llm: LLMBase):
        generate_repository_summary(llm, self)

    def get_summary(self):
        db = SummaryDB(self.repo_path)
        nodes = db.list_nodes()
        db.close()
        return nodes

    def get_summary_tree(self):
        nodes = self.get_summary()
        print(nodes)
        if not nodes:
            tree = None
        else:
            tree = build_tree(nodes)
        return tree
    
    #---------------#
    #    Insight    #
    #---------------#

    def generate_future_suggestion(self, llm: LLMBase, requirements: str = None, max_commits: int = None):
        commit_history = self.get_historical_commit_messages(limit=max_commits)
        code_summary = self.get_summary()
        insights = generate_future_suggestion(requirements, commit_history, code_summary, llm)
        return insights
    
    #--------------#
    #    Commit    #
    #--------------#

    def valid_latest_commit(self):
        db = self.get_commits_db()
        diffs = self.diff_with_head()
        diff_dicts = []
        
        for d in diffs:
            diff_dicts.append({
                "file_path": d.file_path,
                "is_new_file": d.is_new_file,
                "is_deleted_file": d.is_deleted_file,
                "old_start": d.hunk.old_start,
                "new_start": d.hunk.new_start,
                "old_lines": d.hunk.old_lines,
                "new_lines": d.hunk.new_lines,
            })

        diff_hash = hashlib.sha256(json.dumps(diff_dicts, sort_keys=True).encode("utf-8")).hexdigest()
        last_hash = db.get_last_index_hash()

        return (diff_hash == last_hash, diffs, diff_hash)
    
    def generate_commit_groups(self, llm: LLMBase):
        is_latest, diffs, diff_hash = self.valid_latest_commit()
        if is_latest:
            return
        atomic_diffs = generate_atomic_commits(llm, diffs)
        suggested_groups = generate_suggested_commit_groups_agglomerative(atomic_diffs)
        db = self.get_commits_db()

        db.clear_all_groups()
        db.clear_all_atomic_diffs()
        for d in atomic_diffs:
            db.add_atomic_diff(
                diff_id=d.id,
                file_path=d.file_path,
                is_new_file=d.is_new_file,
                is_deleted_file=d.is_deleted_file,
                old_start=d.hunk.old_start if d.hunk else None,
                new_start=d.hunk.new_start if d.hunk else None,
                old_lines=d.hunk.old_lines if d.hunk else None,
                new_lines=d.hunk.new_lines if d.hunk else None
            )

        for g in suggested_groups:
            db.create_commit_group(g["id"], g["name"])
            db.set_group_diffs(g["id"], [d.id for d in g["diffs"]])

        db.set_last_index_hash(diff_hash)
        db.close()

    def list_commit_groups(self):
        db = self.get_commits_db()
        groups = db.list_commit_groups()
        db.close()
        return groups
    
    def get_commit_group(self, group_id: str):
        db = self.get_commits_db()
        group = db.get_commit_group(group_id)
        db.close()
        return group

    def move_diff_to_group(self, diff_id: str, target_group_id: str):        
        db = self.get_commits_db()
        db.move_diff_to_group(diff_id, target_group_id)
        db.close()

    def create_commit_group(self, group_id: str, name: str):
        db = self.get_commits_db()
        group_id = str(uuid.uuid4())
        db.create_commit_group(group_id, name)
        db.close()
        return
    
    def delete_commit_group(self, group_id: str):
        db = self.get_commits_db()
        db.delete_commit_group(group_id)
        db.close()
        return
    
    def reorder_groups(self, ordered_ids):
        db = self.get_commits_db()
        db.reorder_groups(ordered_ids=ordered_ids)
        db.close()

    def list_atomic_diffs(self) -> Dict[str, Any]:
        db = self.get_commits_db()
        diff_details = db.list_atomic_diffs()
        db.close()
        return diff_details
    
    def get_atomic_diffs(self) -> Dict[str, AtomicDiff]:
        diff_details = self.list_atomic_diffs()
        diffs = {}
        for diff_id, diff_dict in diff_details.items():
            diff = AtomicDiff()
            diff.build_from_dict(diff_dict)
            diffs[diff_id] = diff
        return diffs

    #----------------------#
    #    Commit Message    #
    #----------------------#

    def modify_commit_message(self, group_id: str, message: str):
        db = self.get_commits_db()
        db.modify_commit_message(group_id, message)
        db.close()

    def get_commit_message(self, group_id: str):
        db = self.get_commits_db()
        row = db.get_commit_message(group_id)
        return row
    
    def generate_group_commit_message(self, llm: LLMBase, group_id: str):
        db = self.get_commits_db()
        diff_ids = db.get_diffs_in_group(group_id)

        if not diff_ids:
            db.close()
            return None

        diff_dicts = []
        for diff_id in diff_ids:
            diff = db.get_diff(diff_id)
            if diff:
                diff_dicts.append(diff)

        message = generate_commit_message(llm, diff_dicts)

        db.modify_commit_message(group_id, message)


    def get_commit_messages_list(self):
        messages = [c.message.strip() for c in self.repo.iter_commits()]
        return messages
    
    def label_commits(self, llm: LLMBase):
        messages = self.get_commit_messages_list()
        result = generate_labels(llm, messages)
        return result