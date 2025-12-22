import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestIntegrationSummary(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for integration testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.LLMBase")
    @patch("Repository.repository.generate_repository_summary")
    def test_end_to_end_summary_generation(self, mock_generate_summary, MockLLMBase):
        """
        Integration test: end-to-end summary generation for the test/example repo using a mock LLM.
        """
        mock_llm = MockLLMBase()
        # Simulate successful summary generation
        mock_generate_summary.return_value = None
        try:
            self.repo.generate_summary(mock_llm)
            mock_generate_summary.assert_called_once_with(mock_llm, self.repo)
        except Exception as e:
            self.fail(f"End-to-end summary generation raised an exception: {e}")

if __name__ == "__main__":
    unittest.main()
