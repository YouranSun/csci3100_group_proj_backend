import unittest
import main

class TestMainApp(unittest.TestCase):
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

if __name__ == "__main__":
    unittest.main()
