from typing import Optional

from repository import Repository
from db.repo_db import RepoDB
from pathlib import Path

class RepositoryManager:
    def __init__(self, db: RepoDB):
        self.db = db
        self.repos = {}  # path -> Repository

        # 初始化已存储 repo
        for path, name, _ in self.db.list_repos():
            try:
                self.repos[path] = Repository(path)
            except Exception as e:
                print(f"Failed to load {path}: {e}")

    def add_repository(self, path: str, name: Optional[str] = None):
        path = str(Path(path).resolve())
        name = name or Path(path).name
        repo = Repository(path)
        self.repos[path] = repo
        self.db.add_repo(path, name)
        return {'path': path, 'name': name}

    def get_repository(self, path: str) -> Optional[Repository]:
        return self.repos.get(str(Path(path).resolve()))

    def list_repositories(self) -> list[Repository]:
        return list(self.repos.values())

    def remove_repository(self, path: str):
        path = str(Path(path).resolve())
        self.repos.pop(path, None)
        self.db.remove_repo(path)