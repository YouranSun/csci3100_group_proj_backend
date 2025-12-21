import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestCommitGroupRetrieval(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.CommitsDB")
    def test_commit_group_retrieval(self, MockCommitsDB):
        """
        Test commit group retrieval from the database.
        """
        mock_db = MagicMock()
        MockCommitsDB.return_value = mock_db
        mock_db.list_commit_groups.return_value = [
            {"id": "group1", "name": "Feature"},
            {"id": "group2", "name": "Fix"}
        ]
        groups = self.repo.list_commit_groups()
        self.assertEqual(groups[0]["id"], "group1")
        self.assertEqual(groups[1]["name"], "Fix")
        mock_db.list_commit_groups.assert_called_once_with()
        # mock_db.close.assert_called_once()

if __name__ == "__main__":
    unittest.main()
