import unittest
from fastapi.testclient import TestClient
from router.commits_router import router
from main import app

class TestCommitsRouter(unittest.TestCase):
    def setUp(self):
        app.include_router(router)
        self.client = TestClient(app)

    def test_get_commit_groups(self):
        payload = {
            "repo_path": "test/example"
        }
        response = self.client.post("/commit_groups", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("groups", data)
        self.assertIsInstance(data["groups"], list)

    def test_move_diff(self):
        # MoveDiffRequest: repo_path, diff_id, target_group_id
        payload = {
            "repo_path": "test/example",
            "diff_id": "diff1",
            "target_group_id": "group2"
        }
        response = self.client.post("/commit_groups/move_diff", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "ok")

    def test_create_commit_group(self):
        # CommitGroupRequest: repo_path, name
        payload = {
            "repo_path": "test/example",
            "name": "feature"
        }
        response = self.client.post("/commit_groups", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data["groups"][0])
        self.assertIn("name", data["groups"][0])

    def test_delete_commit_group(self):
        # DeleteGroupRequest: repo_path, group_id
        payload = {
            "repo_path": "test/example",
            "group_id": "group1"
        }
        import json
        response = self.client.delete(
            "/commit_groups/delete",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "ok")

    def test_reorder_groups(self):
        # ReorderGroupsRequest: repo_path, ordered_ids
        payload = {
            "repo_path": "test/example",
            "ordered_ids": ["group2", "group1"]
        }
        response = self.client.post("/commit_groups/reorder", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "ok")

    def test_get_atomic_diffs(self):
        payload = {
            "repo_path": "test/example"
        }
        response = self.client.post("/atomic_diffs", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("diffDetails", data)
        self.assertIsInstance(data["diffDetails"], dict)

    def test_apply_commit_groups(self):
        # ApplyCommitGroupsRequest: repo_path
        payload = {
            "repo_path": "test/example"
        }
        # Ensure commit message exists for the group before applying
        group_resp = self.client.post("/commit_groups", json=payload)
        group_id = group_resp.json()["groups"][0]["id"] if group_resp.json()["groups"] else "group1"
        commit_msg_payload = {"repo_path": "test/example", "group_id": group_id}
        self.client.post("/commit_message/generate", json=commit_msg_payload)
        response = self.client.post("/commit_groups/apply", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "ok")

if __name__ == "__main__":
    unittest.main()
