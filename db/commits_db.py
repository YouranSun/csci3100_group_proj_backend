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
        project_root = Path(__file__).parent.parent.resolve()  # 假设 AbstractDB 在 project/function/
        base_dir = Path(base_dir or project_root / "data")
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
            name TEXT NOT NULL,
            order_index INTEGER NOT NULL
        )
        """)
        # atomic diffs
        c.execute("""
        CREATE TABLE IF NOT EXISTS atomic_diffs (
            diff_id TEXT PRIMARY KEY,
            file_path TEXT NOT NULL,
            is_new_file INTEGER,
            is_deleted_file INTEGER,
            old_start INTEGER,
            new_start INTEGER,
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
        c.execute("SELECT id, name, order_index FROM commit_groups ORDER BY order_index ASC")
        groups = []
        for row in c.fetchall():
            group_id, name, order_index = row
            c.execute("SELECT diff_id FROM commit_group_diffs WHERE group_id=? ORDER BY rowid", (group_id,))
            diffs = [r[0] for r in c.fetchall()]
            groups.append({"id": group_id, "name": name, "order": order_index, "diff_ids": diffs})
        return groups
    
    def get_commit_group(self, group_id):
        c = self.conn.cursor()
        c.execute("SELECT id, name, order_index FROM commit_groups WHERE group_id=? ", (group_id,))
        row = c.fetchone()
        if not row:
            return None
        group_id, name, order_index = row
        c.execute("SELECT diff_id FROM commit_group_diffs WHERE group_id=? ORDER BY rowid", (group_id,))
        diffs = [r[0] for r in c.fetchall()]
        group = {"id": group_id, "name": name, "order": order_index, "diff_ids": diffs}
        return group

    def create_commit_group(self, group_id: str, name: str):
        c = self.conn.cursor()
        c.execute("SELECT COALESCE(MAX(order_index), -1) + 1 FROM commit_groups")
        next_order = c.fetchone()[0]

        c.execute(
            "INSERT INTO commit_groups (id, name, order_index) VALUES (?, ?, ?)",
            (group_id, name, next_order)
        )
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

    def reorder_groups(self, ordered_ids: List[str]):
        c = self.conn.cursor()
        for index, gid in enumerate(ordered_ids):
            c.execute("UPDATE commit_groups SET order_index=? WHERE id=?", (index, gid))
        self.conn.commit()

    def get_commit_message(self, group_id: str):
        c = self.conn.cursor()
        c.execute("SELECT value FROM metadata WHERE key=?", (f"commit_message:{group_id}",))
        row = c.fetchone()
        return row[0] if row else None

    def modify_commit_message(self, group_id: str, message: str):
        c = self.conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            (f"commit_message:{group_id}", message)
        )
        self.conn.commit()

    def get_diffs_in_group(self, group_id: str):
        c = self.conn.cursor()
        c.execute("SELECT diff_id FROM commit_group_diffs WHERE group_id=?", (group_id,))
        diff_ids = [r[0] for r in c.fetchall()]
        return diff_ids

    # ---------------- diff 操作 ----------------
    def add_atomic_diff(self, diff_id: str, file_path: str, is_new_file: bool, is_deleted_file: bool, old_start: int, new_start: int, old_lines: List[str], new_lines: List[str]):
        c = self.conn.cursor()
        print(diff_id, file_path, is_new_file, is_deleted_file, old_start, new_start, old_lines, new_lines)
        c.execute(
            "INSERT OR REPLACE INTO atomic_diffs (diff_id, file_path, is_new_file, is_deleted_file, old_start, new_start, old_lines, new_lines) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (diff_id, file_path, is_new_file, is_deleted_file, old_start, new_start, json.dumps(old_lines), json.dumps(new_lines))
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
        c.execute("SELECT file_path, is_new_file, is_deleted_file, old_start, new_start, old_lines, new_lines FROM atomic_diffs WHERE diff_id=?", (diff_id,))
        row = c.fetchone()
        if row:
            file_path, is_new_file, is_deleted_file, old_start, new_start, old_lines, new_lines = row
            return {"diff_id": diff_id, "file_path": file_path,
                    "is_new_file": is_new_file,
                    "is_deleted_file": is_deleted_file,
                    "old_start": old_start, 
                    "new_start": new_start,
                    "old_lines": json.loads(old_lines),
                    "new_lines": json.loads(new_lines)}
        return None
    
    def list_atomic_diffs(self):        
        c = self.conn.cursor()
        c.execute("SELECT diff_id, file_path, is_new_file, is_deleted_file, old_start, new_start, old_lines, new_lines FROM atomic_diffs")
        diff_details = {}
        for row in c.fetchall():
            diff_id, file_path, is_new_file, is_deleted_file, old_start, new_start, old_lines, new_lines = row
            diff_details[diff_id] = {
                "file_path": file_path,
                "is_new_file": is_new_file,
                "is_deleted_file": is_deleted_file,
                "old_start": old_start,
                "new_start": new_start,
                "old_lines": json.loads(old_lines),
                "new_lines": json.loads(new_lines)
            }
        self.close()
        return diff_details

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
