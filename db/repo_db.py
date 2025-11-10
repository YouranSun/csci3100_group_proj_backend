import sqlite3
from pathlib import Path
import hashlib
from typing import Optional, List, Tuple, Dict

class RepoDB:
    def __init__(self, base_dir: Optional[str] = None):
        """
        base_dir: 所有 repo 存储的基础目录，默认 ~/data
        """
        project_root = Path(__file__).parent.parent.resolve()
        self.base_dir = Path(base_dir or project_root / "data")
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.base_dir / "repositories.db"
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_tables()

    def _init_tables(self):
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS repositories (
            path TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            metadata TEXT
        )
        """)
        self.conn.commit()

    def add_repo(self, path: str, name: str, metadata: Optional[Dict] = None):
        try:
            c = self.conn.cursor()
            meta_str = str(metadata) if metadata else ""
            c.execute("""
            INSERT OR REPLACE INTO repositories (path, name, metadata)
            VALUES (?, ?, ?)
            """, (str(Path(path).resolve()), name, meta_str))
            self.conn.commit()
            print("added")
        except Exception as e:
            import traceback
            print("DB add failed:", e)
            traceback.print_exc()

    def get_repo(self, path: str) -> Optional[Tuple[str, str, str]]:
        c = self.conn.cursor()
        c.execute("SELECT path, name, metadata FROM repositories WHERE path = ?", (str(Path(path).resolve()),))
        row = c.fetchone()
        return row if row else None

    def list_repos(self) -> List[Tuple[str, str, str]]:
        c = self.conn.cursor()
        c.execute("SELECT path, name, metadata FROM repositories")
        return c.fetchall()

    def remove_repo(self, path: str):
        c = self.conn.cursor()
        c.execute("DELETE FROM repositories WHERE path = ?", (str(Path(path).resolve()),))
        self.conn.commit()

    def close(self):
        self.conn.close()