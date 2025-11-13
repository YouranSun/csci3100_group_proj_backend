import sqlite3
from pathlib import Path
from typing import List, Dict
import hashlib
import json

class CommitsDB:
    def __init__(self, git_path: str, base_dir: Path = None):
        self.project_dir = self._get_project_dir(git_path, base_dir)
        self.db_path = self.project_dir / "commits.db"
        self.conn = sqlite3.connect(self.db_path)
        self._init_tables()

    @staticmethod
    def _get_project_dir(git_path: str, base_dir: Path = None) -> Path:
        base_dir = Path(base_dir or Path.home() / ".myapp" / "data")
        base_dir.mkdir(parents=True, exist_ok=True)
        path_bytes = str(Path(git_path).resolve()).encode("utf-8")
        hash_hex = hashlib.sha256(path_bytes).hexdigest()
        project_dir = base_dir / hash_hex
        project_dir.mkdir(exist_ok=True)
        return project_dir

    def _init_tables(self):
        c = self.conn.cursor()
        # commit groups
        c.execute("""
        CREATE TABLE IF NOT EXISTS commit_groups (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
        """)
        # atomic diffs
        c.execute("""
        CREATE TABLE IF NOT EXISTS atomic_diffs (
            diff_id TEXT PRIMARY KEY,
            file TEXT,
            old_lines TEXT,
            new_lines TEXT
        )
        """)
        # group-diff relation
        c.execute("""
        CREATE TABLE IF NOT EXISTS commit_group_diffs (
            group_id TEXT,
            diff_id TEXT,
            PRIMARY KEY(group_id, diff_id),
            FOREIGN KEY(group_id) REFERENCES commit_groups(id),
            FOREIGN KEY(diff_id) REFERENCES atomic_diffs(diff_id)
        )
        """)
        # 保存 index hash
        c.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)
        self.conn.commit()

    # ---------------- group 操作 ----------------
    def list_commit_groups(self) -> List[Dict]:
        c = self.conn.cursor()
        c.execute("SELECT id, name FROM commit_groups")
        groups = []
        for row in c.fetchall():
            group_id, name = row
            c.execute("SELECT diff_id FROM commit_group_diffs WHERE group_id=? ORDER BY rowid", (group_id,))
            diffs = [r[0] for r in c.fetchall()]
            groups.append({"id": group_id, "name": name, "diff_ids": diffs})
        return groups

    def create_commit_group(self, group_id: str, name: str):
        c = self.conn.cursor()
        c.execute("INSERT INTO commit_groups (id, name) VALUES (?, ?)", (group_id, name))
        self.conn.commit()

    def rename_commit_group(self, group_id: str, name: str):
        c = self.conn.cursor()
        c.execute("UPDATE commit_groups SET name=? WHERE id=?", (name, group_id))
        self.conn.commit()

    def delete_commit_group(self, group_id: str):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM commit_group_diffs WHERE group_id=?", (group_id,))
        if c.fetchone()[0] > 0:
            raise ValueError("Cannot delete a non-empty group")
        c.execute("DELETE FROM commit_groups WHERE id=?", (group_id,))
        self.conn.commit()

    # ---------------- diff 操作 ----------------
    def add_atomic_diff(self, diff_id: str, file: str, old_lines: List[str], new_lines: List[str]):
        c = self.conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO atomic_diffs (diff_id, file, old_lines, new_lines) VALUES (?, ?, ?, ?)",
            (diff_id, file, json.dumps(old_lines), json.dumps(new_lines))
        )
        self.conn.commit()

    def set_group_diffs(self, group_id: str, diff_ids: List[str]):
        c = self.conn.cursor()
        c.execute("DELETE FROM commit_group_diffs WHERE group_id=?", (group_id,))
        for diff_id in diff_ids:
            c.execute("INSERT INTO commit_group_diffs (group_id, diff_id) VALUES (?, ?)", (group_id, diff_id))
        self.conn.commit()

    def move_diff_to_group(self, diff_id: str, target_group_id: str):
        c = self.conn.cursor()
        c.execute("DELETE FROM commit_group_diffs WHERE diff_id=?", (diff_id,))
        c.execute("INSERT INTO commit_group_diffs (group_id, diff_id) VALUES (?, ?)", (target_group_id, diff_id))
        self.conn.commit()

    def get_diff(self, diff_id: str):
        c = self.conn.cursor()
        c.execute("SELECT file, old_lines, new_lines FROM atomic_diffs WHERE diff_id=?", (diff_id,))
        row = c.fetchone()
        if row:
            file, old_lines, new_lines = row
            return {"diff_id": diff_id, "file": file,
                    "old_lines": json.loads(old_lines),
                    "new_lines": json.loads(new_lines)}
        return None

    # ---------------- metadata / hash ----------------
    def get_last_index_hash(self) -> str:
        c = self.conn.cursor()
        c.execute("SELECT value FROM metadata WHERE key='index_hash'")
        row = c.fetchone()
        return row[0] if row else None

    def set_last_index_hash(self, diff_hash: str):
        c = self.conn.cursor()
        c.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES ('index_hash', ?)", (diff_hash,))
        self.conn.commit()

    # ---------------- 清空 ----------------
    def clear_all_groups(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM commit_group_diffs")
        c.execute("DELETE FROM commit_groups")
        self.conn.commit()

    def clear_all_atomic_diffs(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM atomic_diffs")
        self.conn.commit()

    def close(self):
        self.conn.close()
