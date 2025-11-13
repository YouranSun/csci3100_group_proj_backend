# function/abstract_db.py
import sqlite3
from pathlib import Path
import hashlib
from typing import Optional, List, Tuple

class SummaryDB:
    def __init__(self, git_path: str, base_dir: Optional[str] = None):
        """
        git_path: 项目 .git 根目录
        base_dir: 所有项目存储的基础目录，默认 ~/.myapp/data
        """
        self.project_dir = self._get_project_dir(git_path, base_dir)
        self.db_path = self.project_dir / "repo_abstracts.db"
        self.conn = sqlite3.connect(self.db_path)
        self._init_tables()

    @staticmethod
    def _get_project_dir(git_path: str, base_dir: Optional[str] = None) -> Path:
        project_root = Path(__file__).parent.parent.resolve()  # 假设 AbstractDB 在 project/function/
        base_dir = Path(base_dir or project_root / "data")
        base_dir.mkdir(parents=True, exist_ok=True)

        # SHA256 哈希 .git 路径
        path_bytes = str(Path(git_path).resolve()).encode("utf-8")
        hash_hex = hashlib.sha256(path_bytes).hexdigest()

        project_dir = base_dir / hash_hex
        project_dir.mkdir(exist_ok=True)
        print(project_dir)
        return project_dir

    def _init_tables(self):
        """初始化表"""
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS abstracts (
            path TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            summary TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def save_node(self, path: str, node_type: str, summary: str):
        """保存单个节点摘要"""
        c = self.conn.cursor()
        c.execute("""
        INSERT OR REPLACE INTO abstracts (path, type, summary)
        VALUES (?, ?, ?)
        """, (path, node_type, summary))
        self.conn.commit()

    def get_node(self, path: str) -> Optional[Tuple[str, str]]:
        """获取单个节点摘要"""
        c = self.conn.cursor()
        c.execute("SELECT type, summary FROM abstracts WHERE path = ?", (path,))
        row = c.fetchone()
        return row if row else None

    def list_nodes(self) -> List[Tuple[str, str, str]]:
        """列出所有节点"""
        c = self.conn.cursor()
        c.execute("SELECT path, type, summary FROM abstracts")
        return c.fetchall()
    
    def clear_all_nodes(self):
        self.cursor.execute("DELETE FROM abstracts")
        self.conn.commit()

    def close(self):
        self.conn.close()