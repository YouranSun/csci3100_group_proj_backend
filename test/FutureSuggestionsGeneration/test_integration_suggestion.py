import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestIntegrationSuggestion(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for integration testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.LLMBase")
    @patch("Repository.repository.generate_future_suggestion")
    def test_generate_suggestions_with_and_without_requirements(self, mock_generate_suggestion, MockLLMBase):
        """
        Integration test: generate suggestions with and without user requirements using a mock LLM.
        """
        mock_llm = MockLLMBase()
        # Simulate LLM returning suggestions
        mock_generate_suggestion.side_effect = [
            [{"description": "Refactor code", "priority": "Medium"}],
            [{"description": "Add docs", "priority": "Low"}]
        ]
        # Without requirements
        result_no_req = self.repo.generate_future_suggestion(mock_llm)
        self.assertEqual(result_no_req[0]["description"], "Refactor code")
        # With requirements
        result_with_req = self.repo.generate_future_suggestion(mock_llm, requirements="Add documentation")
        self.assertEqual(result_with_req[0]["description"], "Add docs")
        self.assertEqual(mock_generate_suggestion.call_count, 2)

if __name__ == "__main__":
    unittest.main()
