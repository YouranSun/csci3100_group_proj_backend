from typing import Optional
from Repository.repository import Repository
from db.repo_db import RepoDB
from pathlib import Path

class RepositoryManager:
    def __init__(self, db: RepoDB):
        self.db = db
        self.paths = []

        for path, name, _ in self.db.list_repos():
            abs_path = str(Path(path).resolve())
            self.paths.append(abs_path)

    def add_repository(self, path: str, name: Optional[str] = None):
        abs_path = str(Path(path).resolve())
        name = name or Path(abs_path).name

        if abs_path not in self.paths:
            self.paths.append(abs_path)
            self.db.add_repo(abs_path, name)

        return {"path": abs_path, "name": name}

    def get_repository(self, path: str) -> Optional[Repository]:
        abs_path = str(Path(path).resolve())
        if abs_path not in self.paths:
            return None

        try:
            return Repository(abs_path)
        except Exception as e:
            print(f"Failed to open repo {abs_path}: {e}")
            return None

    def list_repositories(self):
        return [
            {"path": path, "name": Path(path).name}
            for path in self.paths
        ]

    def remove_repository(self, path: str):
        abs_path = str(Path(path).resolve())
        if abs_path in self.paths:
            self.paths.remove(abs_path)
            self.db.remove_repo(abs_path)
