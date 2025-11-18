import unittest
from fastapi.testclient import TestClient
import main

class DummyRepo:
    def __init__(self, repo_path):
        self.repo_path = repo_path
    def get_summary_tree(self):
        return {"root": "tree"}
    def generate_summary(self, llm): pass

class DummyLLM:
    def __init__(self, model): pass

class DummyGetSummaryRequest:
    def __init__(self, repo_path):
        self.repo_path = repo_path

class DummyRefreshSummaryRequest:
    def __init__(self, repo_path):
        self.repo_path = repo_path

def patch_deps():
    import sys
    sys.modules["Repository.repository"] = type("mod", (), {"Repository": DummyRepo})
    sys.modules["llm.openai_llm"] = type("mod", (), {"OpenAILLM": DummyLLM})
    sys.modules["router.router_request"] = type("mod", (), {
        "GetSummaryRequest": DummyGetSummaryRequest,
        "RefreshSummaryRequest": DummyRefreshSummaryRequest
    })

class TestSummaryRouter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch_deps()
        cls.client = TestClient(main.app)

    def test_get_summary(self):
        req = {"repo_path": "repo"}
        response = self.client.post("/summary", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("tree", response.json())

    def test_refresh_summary(self):
        req = {"repo_path": "repo"}
        response = self.client.post("/summary/refresh", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("tree", response.json())
        self.assertIn("message", response.json())

if __name__ == "__main__":
    unittest.main()
