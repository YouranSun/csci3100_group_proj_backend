import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestErrorCases(unittest.TestCase):
    def setUp(self):
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.SummaryDB")
    def test_repo_unreadable(self, MockSummaryDB):
        """
        Test handling of unreadable repository (e.g., DB error).
        """
        MockSummaryDB.side_effect = Exception("DB error")
        with self.assertRaises(Exception) as context:
            self.repo.get_summary()
        self.assertIn("DB error", str(context.exception))

    @patch("Repository.repository.LLMBase")
    @patch("Repository.repository.generate_future_suggestion")
    def test_llm_failure(self, mock_generate_suggestion, MockLLMBase):
        """
        Test handling of LLM failure during suggestion generation.
        """
        mock_llm = MockLLMBase()
        mock_generate_suggestion.side_effect = Exception("LLM failure")
        with self.assertRaises(Exception) as context:
            self.repo.generate_future_suggestion(mock_llm)
        self.assertIn("LLM failure", str(context.exception))

if __name__ == "__main__":
    unittest.main()
