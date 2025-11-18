import unittest
import tempfile
import os
from db.user_db import UserDB

class TestUserDB(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "user_db.sqlite3")
        self.db = UserDB(db_path=self.db_path)

    def tearDown(self):
        self.db.close()
        os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_add_and_get_user(self):
        result = self.db.add_user("alice", "password123")
        self.assertTrue(result)
        user = self.db.get_user("alice")
        self.assertIsNotNone(user)
        self.assertEqual(user[1], "alice")

    def test_add_duplicate_user(self):
        self.db.add_user("bob", "pw")
        result = self.db.add_user("bob", "pw2")
        self.assertFalse(result)

    def test_verify_user(self):
        self.db.add_user("carol", "mypw")
        self.assertTrue(self.db.verify_user("carol", "mypw"))
        self.assertFalse(self.db.verify_user("carol", "wrongpw"))
        self.assertFalse(self.db.verify_user("notexist", "pw"))

    def test_list_users(self):
        self.db.add_user("dave", "pw1")
        self.db.add_user("eve", "pw2")
        users = self.db.list_users()
        usernames = [u[1] for u in users]
        self.assertIn("dave", usernames)
        self.assertIn("eve", usernames)

if __name__ == "__main__":
    unittest.main()
