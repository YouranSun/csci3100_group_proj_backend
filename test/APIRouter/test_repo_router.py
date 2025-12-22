import unittest
from fastapi.testclient import TestClient
from router.repo_router import router
from main import app

class TestRepoRouter(unittest.TestCase):
    def setUp(self):
        app.include_router(router)
        self.client = TestClient(app)

    def test_list_repos(self):
        response = self.client.get("/repos")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_add_repo(self):
        payload = {
            "repo_path": "test/example",
            "name": "example",
            "path": "test/example"
        }
        response = self.client.post("/repos", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("path", data)
        self.assertTrue(data["path"])
if __name__ == "__main__":
    unittest.main()
