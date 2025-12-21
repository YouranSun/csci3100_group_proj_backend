import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestRepositoryHash(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.CommitsDB")
    def test_valid_latest_commit_hash(self, MockCommitsDB):
        """
        Test that valid_latest_commit correctly computes and compares the diff hash.
        """
        # Mock DB to return a specific last_index_hash
        mock_db = MagicMock()
        MockCommitsDB.return_value = mock_db

        # Simulate diff_with_head returning deterministic diffs
        fake_diff = MagicMock()
        fake_diff.file_path = "main.py"
        fake_diff.is_new_file = False
        fake_diff.is_deleted_file = False
        fake_diff.hunk.old_start = 1
        fake_diff.hunk.new_start = 1
        fake_diff.hunk.old_lines = 1
        fake_diff.hunk.new_lines = 1

        self.repo.diff_with_head = MagicMock(return_value=[fake_diff])

        # Compute expected hash
        import hashlib, json
        diff_dicts = [{
            "file_path": "main.py",
            "is_new_file": False,
            "is_deleted_file": False,
            "old_start": 1,
            "new_start": 1,
            "old_lines": 1,
            "new_lines": 1,
        }]
        expected_hash = hashlib.sha256(json.dumps(diff_dicts, sort_keys=True).encode("utf-8")).hexdigest()
        mock_db.get_last_index_hash.return_value = expected_hash

        # Should return (True, diffs, hash)
        is_latest, diffs, diff_hash = self.repo.valid_latest_commit()
        self.assertTrue(is_latest)
        self.assertEqual(diff_hash, expected_hash)
        self.assertEqual(len(diffs), 1)
        # Assert that get_last_index_hash was called once with no arguments
        mock_db.get_last_index_hash.assert_called_once_with()
        # Assert that diff_with_head was called (mocked as MagicMock)
        self.repo.diff_with_head.assert_called_once_with()

if __name__ == "__main__":
    unittest.main()
