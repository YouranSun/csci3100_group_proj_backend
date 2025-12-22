import unittest
from fastapi.testclient import TestClient
from router.user_router import router
from main import app

class TestUserRouter(unittest.TestCase):
    def setUp(self):
        app.include_router(router)
        self.client = TestClient(app)

    def test_register(self):
        payload = {
            "username": "testuser",
            "password": "testpass",
        }
        response = self.client.post("/user/register", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["username"], "testuser")

    def test_login(self):
        payload = {
            "username": "testuser",
            "password": "testpass"
        }
        response = self.client.post("/user/login", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # self.assertIn("token", data)
        # self.assertTrue(data["token"])
        self.assertIn("message", data)
        self.assertIn("Login successful", data["message"])

    def test_logout(self):
        response = self.client.post("/user/logout")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertTrue(data["message"])

    def test_get_me(self):
        response = self.client.get("/user/me", cookies={"user": "testuser"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("username", data)

if __name__ == "__main__":
    unittest.main()
