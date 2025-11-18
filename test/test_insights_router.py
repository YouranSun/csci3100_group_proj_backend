import unittest
from fastapi.testclient import TestClient
import main

class DummyRepo:
    def __init__(self, repo_path):
        self.repo_path = repo_path
    def generate_future_suggestion(self, llm, requirements, max_commits):
        return {"insights": ["suggestion1", "suggestion2"]}

class DummyLLM:
    def __init__(self, model): pass

class DummyFutureSuggestionsRequest:
    def __init__(self, repo_path, requirements=None, max_commits=None):
        self.repo_path = repo_path
        self.requirements = requirements
        self.max_commits = max_commits

def patch_deps():
    import sys
    sys.modules["Repository.repository"] = type("mod", (), {"Repository": DummyRepo})
    sys.modules["llm.openai_llm"] = type("mod", (), {"OpenAILLM": DummyLLM})
    sys.modules["router.router_request"] = type("mod", (), {
        "FutureSuggestionsRequest": DummyFutureSuggestionsRequest
    })

class TestInsightsRouter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch_deps()
        cls.client = TestClient(main.app)

    def test_generate_future_suggestions(self):
        req = {"repo_path": "repo", "requirements": "Improve", "max_commits": 5}
        response = self.client.post("/insights", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("insights", response.json())

if __name__ == "__main__":
    unittest.main()
