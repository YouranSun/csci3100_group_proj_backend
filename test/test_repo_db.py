import unittest
import tempfile
import shutil
from pathlib import Path
from db.repo_db import RepoDB

class TestRepoDB(unittest.TestCase):
    def setUp(self):
        self.db = RepoDB(base_dir=":memory:")

    def tearDown(self):
        self.db.close()

    def test_add_and_get_repo(self):
        repo_path = "repo1"
        self.db.add_repo(repo_path, "repo1", {"desc": "test"})
        repo = self.db.get_repo(repo_path)
        self.assertIsNotNone(repo)
        self.assertEqual(repo[1], "repo1")
        self.assertIn("desc", repo[2])

    def test_list_repos(self):
        repo_path1 = "repoA"
        repo_path2 = "repoB"
        self.db.add_repo(repo_path1, "repoA")
        self.db.add_repo(repo_path2, "repoB")
        repos = self.db.list_repos()
        self.assertEqual(len(repos), 2)
        names = [r[1] for r in repos]
        self.assertIn("repoA", names)
        self.assertIn("repoB", names)

    def test_remove_repo(self):
        repo_path = "repo2"
        self.db.add_repo(repo_path, "repo2")
        self.db.remove_repo(repo_path)
        repo = self.db.get_repo(repo_path)
        self.assertIsNone(repo)

if __name__ == "__main__":
    unittest.main()
