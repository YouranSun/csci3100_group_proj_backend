import sqlite3
from pathlib import Path
from typing import Optional, Tuple
import bcrypt 

class UserDB:
    def __init__(self, db_path: str = "data/user.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        """
        self.conn.execute(sql)
        self.conn.commit()

    def add_user(self, username: str, password: str) -> bool:
        """返回 True 表示添加成功，False 表示用户已存在"""
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        try:
            self.conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, username: str) -> Optional[Tuple[int, str, str]]:
        """返回 (id, username, password_hash) 或 None"""
        cur = self.conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,)
        )
        row = cur.fetchone()
        return (row["id"], row["username"], row["password_hash"]) if row else None

    def verify_user(self, username: str, password: str) -> bool:
        """校验用户名密码"""
        user = self.get_user(username)
        if not user:
            return False
        stored_hash = user[2].encode()
        return bcrypt.checkpw(password.encode(), stored_hash)

    def list_users(self):
        """返回所有用户 [(id, username), ...]"""
        cur = self.conn.execute("SELECT id, username FROM users")
        return [(row["id"], row["username"]) for row in cur.fetchall()]

    def close(self):
        self.conn.close()
