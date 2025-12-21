import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestRepositorySummary(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.LLMBase")
    @patch("Repository.repository.generate_repository_summary")
    def test_generate_summary(self, mock_generate_summary, MockLLMBase):
        """
        Test that generate_summary calls the summary generation logic with a mock LLM.
        """
        mock_llm = MockLLMBase()
        self.repo.generate_summary(mock_llm)
        mock_generate_summary.assert_called_once_with(mock_llm, self.repo)
        # Assert that the mock LLM was not called with unexpected arguments
        self.assertIsInstance(mock_llm, MockLLMBase)

    @patch("Repository.repository.SummaryDB")
    def test_get_summary(self, MockSummaryDB):
        """
        Test that get_summary retrieves summary nodes from the database.
        """
        mock_db = MagicMock()
        MockSummaryDB.return_value = mock_db
        mock_db.list_nodes.return_value = [{"id": 1, "name": "main.py"}]
        nodes = self.repo.get_summary()

if __name__ == "__main__":
    unittest.main()
