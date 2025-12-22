import unittest
from fastapi.testclient import TestClient
from router.insights_router import router
from main import app

class TestInsightsRouter(unittest.TestCase):
    def setUp(self):
        app.include_router(router)
        self.client = TestClient(app)

    def test_generate_future_suggestions(self):
        payload = {
            "repo_path": "test/example",
            "requirements": "Add new feature",
            "max_commits": 50
        }
        response = self.client.post("/insights", json=payload)
        self.assertEqual(response.status_code, 200)
        import json
        data = response.json()
        if isinstance(data, str):
            data = json.loads(data)
        self.assertIsInstance(data, list)
        if data:
            suggestion = data[0]
            self.assertIn("title", suggestion)
            self.assertIn("description", suggestion)
        # Test edge case: empty requirements
        payload2 = {
            "repo_path": "test/example",
            "requirements": "",
            "max_commits": 50
        }
        response2 = self.client.post("/insights", json=payload2)
        self.assertEqual(response2.status_code, 200)
        import json
        data2 = response2.json()
        if isinstance(data2, str):
            data2 = json.loads(data2)
        self.assertIsInstance(data2, list)
if __name__ == "__main__":
    unittest.main()
