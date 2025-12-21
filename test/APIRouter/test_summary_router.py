import unittest
from fastapi.testclient import TestClient
from router.summary_router import router
from main import app

class TestSummaryRouter(unittest.TestCase):
    def setUp(self):
        app.include_router(router)
        self.client = TestClient(app)

    def test_get_summary(self):
        payload = {
            "repo_path": "test/example"
        }
        response = self.client.post("/summary", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("tree", data)
        self.assertIsInstance(data["tree"], list)

    def test_refresh_summary(self):
        payload = {
            "repo_path": "test/example"
        }
        response = self.client.post("/summary/refresh", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertTrue(data["message"])
if __name__ == "__main__":
    unittest.main()
