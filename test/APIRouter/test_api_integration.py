import unittest
from fastapi.testclient import TestClient
from main import app

class TestAPIIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_repo_summary_workflow(self):
        payload = {"repo_path": "test/example"}
        r1 = self.client.post("/summary", json=payload)
        self.assertEqual(r1.status_code, 200)
        data1 = r1.json()
        self.assertIn("tree", data1)
        self.assertIsInstance(data1["tree"], list)
        r2 = self.client.post("/summary/refresh", json=payload)
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        self.assertIn("message", data2)
        self.assertIsInstance(data2["message"], str)
        self.assertTrue(data2["message"])

    def test_commit_split_group_apply_workflow(self):
        payload = {"repo_path": "test/example"}
        r1 = self.client.post("/commit_groups", json=payload)
        self.assertEqual(r1.status_code, 200)
        self.assertIn("groups", r1.json())
        group_id = r1.json()["groups"][0]["id"] if r1.json()["groups"] else "group1"
        move_payload = {"repo_path": "test/example", "diff_id": "diff1", "target_group_id": group_id}
        r2 = self.client.post("/commit_groups/move_diff", json=move_payload)
        self.assertEqual(r2.status_code, 200)
        self.assertIn("status", r2.json())
        reorder_payload = {"repo_path": "test/example", "ordered_ids": [group_id]}
        r3 = self.client.post("/commit_groups/reorder", json=reorder_payload)
        self.assertEqual(r3.status_code, 200)
        self.assertIn("status", r3.json())
        # Ensure commit message exists for the group before applying
        commit_msg_payload = {"repo_path": "test/example", "group_id": group_id}
        self.client.post("/commit_message/generate", json=commit_msg_payload)
        apply_payload = {"repo_path": "test/example"}
        r4 = self.client.post("/commit_groups/apply", json=apply_payload)
        self.assertEqual(r4.status_code, 200)
        self.assertIn("status", r4.json())

    def test_commit_message_workflow(self):
        payload = {"repo_path": "test/example", "group_id": "group1"}
        r1 = self.client.post("/commit_message/generate", json=payload)
        self.assertEqual(r1.status_code, 200)
        self.assertIn("message", r1.json())
        r2 = self.client.post("/commit_message", json=payload)
        self.assertEqual(r2.status_code, 200)
        self.assertIn("message", r2.json())
        edit_payload = {"repo_path": "test/example", "group_id": "group1", "message": "New commit message"}
        r3 = self.client.post("/commit_message/edit", json=edit_payload)
        self.assertEqual(r3.status_code, 200)
        self.assertIn("message", r3.json())

    def test_future_suggestion_workflow(self):
        payload = {"repo_path": "test/example", "requirements": "Add new feature", "max_commits": 50}
        r = self.client.post("/insights", json=payload)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json())

    def test_user_auth_workflow(self):
        reg_payload = {"username": "testuser", "password": "testpass"}
        r1 = self.client.post("/user/register", json=reg_payload)
        self.assertEqual(r1.status_code, 200)
        # skip since token is not realized at this moment

    def test_repo_management_workflow(self):
        r1 = self.client.get("/repos")
        self.assertEqual(r1.status_code, 200)
        self.assertIsInstance(r1.json(), list)
        add_payload = {"repo_path": "test/example", "name": "example", "path": "test/example"}
        r2 = self.client.post("/repos", json=add_payload)
        self.assertEqual(r2.status_code, 200)
        self.assertIn("path", r2.json())

if __name__ == "__main__":
    unittest.main()
