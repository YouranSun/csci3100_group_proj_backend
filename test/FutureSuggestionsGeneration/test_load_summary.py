import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestLoadSummary(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.SummaryDB")
    def test_loading_and_validating_repo_summary(self, MockSummaryDB):
        """
        Test loading and validating repository summary from the database.
        """
        mock_db = MagicMock()
        MockSummaryDB.return_value = mock_db
        mock_db.list_nodes.return_value = [{"id": 1, "name": "main.py"}]
        nodes = self.repo.get_summary()
        self.assertEqual(nodes, [{"id": 1, "name": "main.py"}])
        mock_db.close.assert_called_once()

if __name__ == "__main__":
    unittest.main()
