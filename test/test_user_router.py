import unittest
from fastapi.testclient import TestClient
from router import user_router

class DummyUserDB:
    def __init__(self):
        self.users = {"u": ("1", "u", "p")}
    def add_user(self, username, password):
        if username in self.users:
            return False
        self.users[username] = (str(len(self.users)+1), username, password)
        return True
    def get_user(self, username):
        return self.users.get(username)
    def verify_user(self, username, password):
        return self.users.get(username, [None, None, None])[2] == password

class DummyUserRegisterRequest:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class DummyUserLoginRequest:
    def __init__(self, username, password):
        self.username = username
        self.password = password

class DummyUserResponse:
    def __init__(self, id, username):
        self.id = id
        self.username = username

def patch_deps():
    import sys
    sys.modules["db.user_db"] = type("mod", (), {"UserDB": lambda: DummyUserDB()})
    sys.modules["router.router_request"] = type("mod", (), {
        "UserRegisterRequest": DummyUserRegisterRequest,
        "UserLoginRequest": DummyUserLoginRequest,
        "UserResponse": DummyUserResponse
    })

class TestUserRouter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch_deps()
        cls.client = TestClient(user_router.router)

    def test_register(self):
        req = {"username": "newuser", "password": "pw"}
        response = self.client.post("/user/register", json=req)
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.json())

    def test_register_duplicate(self):
        req = {"username": "u", "password": "pw"}
        response = self.client.post("/user/register", json=req)
        self.assertEqual(response.status_code, 400)

    def test_login_logout_me(self):
        req = {"username": "u", "password": "p"}
        response = self.client.post("/user/login", json=req)
        self.assertEqual(response.status_code, 200)
        cookies = response.cookies
        response2 = self.client.get("/user/me", cookies=cookies)
        self.assertEqual(response2.status_code, 200)
        self.assertIn("username", response2.json())
        response3 = self.client.post("/user/logout", cookies=cookies)
        self.assertEqual(response3.status_code, 200)
        response4 = self.client.get("/user/me")
        self.assertEqual(response4.status_code, 401)

if __name__ == "__main__":
    unittest.main()
