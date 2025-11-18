import unittest
from fastapi.testclient import TestClient
import main

class DummyRepo:
    def __init__(self, repo_path):
        self.repo_path = repo_path
    def generate_commit_groups(self, llm): pass
    def list_commit_groups(self): return [{"id": "g1", "name": "Group1", "diff_ids": []}]
    def move_diff_to_group(self, diff_id, target_group_id): pass
    def create_commit_group(self, group_id, name): pass
    def get_commit_group(self, group_id): return {"id": group_id, "name": "Group", "diff_ids": []}
    def delete_commit_group(self, group_id): pass
    def reorder_groups(self, ordered_ids): pass
    def list_atomic_diffs(self): return {"d1": {"file_path": "foo.py"}}
    def apply_commit_groups(self): return [{"group_id": "g1", "message": "msg", "num_diffs": 1}]

class DummyLLM:
    def __init__(self, model): pass

class DummyReq:
    def __init__(self, repo_path, group_id=None, name=None, diff_id=None, target_group_id=None, ordered_ids=None):
        self.repo_path = repo_path
        self.group_id = group_id
        self.name = name
        self.diff_id = diff_id
        self.target_group_id = target_group_id
        self.ordered_ids = ordered_ids

def patch_deps():
    import sys
    sys.modules["Repository.repository"] = type("mod", (), {"Repository": DummyRepo})
    sys.modules["llm.openai_llm"] = type("mod", (), {"OpenAILLM": DummyLLM})
    sys.modules["router.router_request"] = type("mod", (), {
        "GetCommitGroupsRequest": DummyReq,
        "CommitGroupRequest": DummyReq,
        "DeleteGroupRequest": DummyReq,
        "ApplyCommitGroupsRequest": DummyReq,
        "ReorderGroupsRequest": DummyReq,
        "MoveDiffRequest": DummyReq,
        "GetAtomicDiffsRequest": DummyReq
    })

class TestCommitsRouter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch_deps()
        cls.client = TestClient(main.app)

    def test_get_commit_groups(self):
        req = {"repo_path": "repo"}
        response = self.client.post("/commit_groups", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("groups", response.json())

    def test_move_diff(self):
        req = {"repo_path": "repo", "diff_id": "d1", "target_group_id": "g2"}
        response = self.client.post("/commit_groups/move_diff", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_create_commit_group(self):
        req = {"repo_path": "repo", "group_id": "g2", "name": "Group2"}
        response = self.client.post("/commit_groups", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], "g2")

    def test_delete_commit_group(self):
        req = {"repo_path": "repo", "group_id": "g1"}
        response = self.client.delete("/commit_groups/delete", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_reorder_groups(self):
        req = {"repo_path": "repo", "ordered_ids": ["g1", "g2"]}
        response = self.client.post("/commit_groups/reorder", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_get_atomic_diffs(self):
        req = {"repo_path": "repo"}
        response = self.client.post("/atomic_diffs", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("diffDetails", response.json())

    def test_commit_groups(self):
        req = {"repo_path": "repo"}
        response = self.client.post("/commit_groups/apply", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertIn("result", response.json())

if __name__ == "__main__":
    unittest.main()
