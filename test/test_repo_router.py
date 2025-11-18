import unittest
from fastapi.testclient import TestClient
import main

class DummyRepoDB:
    def close(self): pass

class DummyRepositoryManager:
    def __init__(self, db): pass
    def list_repositories(self): return [{"path": "p1", "name": "repo1"}]
    def add_repository(self, path, name=None): return {"path": path, "name": name or "repo"}

class DummyAddRepoRequest:
    def __init__(self, path, name=None):
        self.path = path
        self.name = name

def patch_deps():
    import sys
    sys.modules["db.repo_db"] = type("mod", (), {"RepoDB": DummyRepoDB})
    sys.modules["Repository.repository_manager"] = type("mod", (), {"RepositoryManager": DummyRepositoryManager})
    sys.modules["router.router_request"] = type("mod", (), {"AddRepoRequest": DummyAddRepoRequest})

class TestRepoRouter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch_deps()
        cls.client = TestClient(main.app)

    def test_list_repos(self):
        response = self.client.get("/repos")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), list))
        self.assertEqual(response.json()[0]["name"], "repo1")

    def test_add_repo(self):
        req = {"path": "p2", "name": "repo2"}
        response = self.client.post("/repos", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["path"], "p2")
        self.assertEqual(response.json()["name"], "repo2")

if __name__ == "__main__":
    unittest.main()
