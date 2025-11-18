import unittest
from Repository import repository_manager

class DummyRepoDB:
    def __init__(self):
        self.repos = []
    def list_repos(self):
        return [("path1", "repo1", None)]
    def add_repo(self, path, name):
        self.repos.append((path, name))
    def remove_repo(self, path):
        self.repos = [r for r in self.repos if r[0] != path]

class DummyRepository:
    def __init__(self, path):
        self.path = path

def patch_deps():
    import sys
    sys.modules["Repository.repository"] = type("mod", (), {
        "Repository": DummyRepository
    })

class TestRepositoryManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch_deps()

    def test_add_and_list_repository(self):
        db = DummyRepoDB()
        mgr = repository_manager.RepositoryManager(db)
        mgr.add_repository("path2", "repo2")
        repos = mgr.list_repositories()
        self.assertTrue(any(r["path"].endswith("path2") for r in repos))

    def test_get_repository(self):
        db = DummyRepoDB()
        mgr = repository_manager.RepositoryManager(db)
        mgr.add_repository("path3", "repo3")
        repo = mgr.get_repository("path3")
        self.assertIsNotNone(repo)
        self.assertTrue(hasattr(repo, "path"))

    def test_remove_repository(self):
        db = DummyRepoDB()
        mgr = repository_manager.RepositoryManager(db)
        mgr.add_repository("path4", "repo4")
        mgr.remove_repository("path4")
        repos = mgr.list_repositories()
        self.assertFalse(any(r["path"].endswith("path4") for r in repos))

if __name__ == "__main__":
    unittest.main()
