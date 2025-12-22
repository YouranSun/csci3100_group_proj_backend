import unittest
from fastapi.testclient import TestClient
from router.commit_message_router import router
from main import app

class TestCommitMessageRouter(unittest.TestCase):
    def setUp(self):
        app.include_router(router)
        self.client = TestClient(app)

    def test_generate_group_commit_message(self):
        payload = {
            "repo_path": "test/example",
            "group_id": "group1"
        }
        response = self.client.post("/commit_message/generate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertTrue(data["message"])

    def test_get_commit_message(self):
        payload = {
            "repo_path": "test/example",
            "group_id": "group1"
        }
        response = self.client.post("/commit_message", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertTrue(data["message"])

    def test_edit_commit_message(self):
        payload = {
            "repo_path": "test/example",
            "group_id": "group1",
            "message": "New commit message"
        }
        response = self.client.post("/commit_message/edit", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertTrue(data["message"])
if __name__ == "__main__":
    unittest.main()
