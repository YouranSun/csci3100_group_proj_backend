import unittest
from fastapi.testclient import TestClient
import main

class TestMainApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def test_app_instance(self):
        self.assertTrue(hasattr(main, "app"))
        self.assertEqual(main.app.title, "FastAPI")

    def test_cors_middleware(self):
        middlewares = [mw.cls.__name__ for mw in main.app.user_middleware]
        self.assertIn("CORSMiddleware", middlewares)

    def test_router_registered(self):
        routes = [r.path for r in main.app.routes]
        self.assertIn("/repos", routes)
        self.assertIn("/summary", routes)
        self.assertIn("/commit_groups", routes)
        self.assertIn("/commit_message", routes)
        self.assertIn("/insights", routes)
        self.assertTrue(any("/user" in r for r in routes))

    def test_repos_endpoint(self):
        response = self.client.get("/repos")
        self.assertIn(response.status_code, [200, 422])  # 422 if missing dependencies

if __name__ == "__main__":
    unittest.main()
