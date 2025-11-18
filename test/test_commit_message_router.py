import unittest
from fastapi.testclient import TestClient
from router import commit_message_router

class DummyRepo:
    def __init__(self, repo_path):
        self.repo_path = repo_path
    def generate_group_commit_message(self, llm, group_id): pass
    def get_commit_message(self, group_id): return ("msg",)
    def modify_commit_message(self, group_id, message): pass

class DummyLLM:
    def __init__(self, model): pass

class DummyCommitMessageRequest:
    def __init__(self, repo_path, group_id):
        self.repo_path = repo_path
        self.group_id = group_id

class DummyEditCommitMessageRequest:
    def __init__(self, repo_path, group_id, message):
        self.repo_path = repo_path
        self.group_id = group_id
        self.message = message

def patch_deps():
    import sys
    sys.modules["Repository.repository"] = type("mod", (), {"Repository": DummyRepo})
    sys.modules["llm.openai_llm"] = type("mod", (), {"OpenAILLM": DummyLLM})
    sys.modules["router.router_request"] = type("mod", (), {
        "CommitMessageRequest": DummyCommitMessageRequest,
        "EditCommitMessageRequest": DummyEditCommitMessageRequest
    })

class TestCommitMessageRouter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch_deps()
        cls.client = TestClient(commit_message_router.router)

    def test_generate_group_commit_message(self):
        req = {"repo_path": "repo", "group_id": "gid"}
        response = self.client.post("/commit_message/generate", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["group_id"], "gid")
        self.assertEqual(response.json()["message"], "msg")

    def test_get_commit_message(self):
        req = {"repo_path": "repo", "group_id": "gid"}
        response = self.client.post("/commit_message", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["group_id"], "gid")
        self.assertEqual(response.json()["message"], "msg")

    def test_edit_commit_message(self):
        req = {"repo_path": "repo", "group_id": "gid", "message": "newmsg"}
        response = self.client.post("/commit_message/edit", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["group_id"], "gid")
        self.assertEqual(response.json()["message"], "newmsg")

if __name__ == "__main__":
    unittest.main()
