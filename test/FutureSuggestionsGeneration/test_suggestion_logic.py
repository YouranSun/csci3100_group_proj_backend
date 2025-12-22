import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestSuggestionLogic(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.LLMBase")
    @patch("Repository.repository.generate_future_suggestion")
    def test_suggestion_generation_logic(self, mock_generate_suggestion, MockLLMBase):
        """
        Test suggestion generation logic using a mock LLM.
        """
        mock_llm = MockLLMBase()
        mock_generate_suggestion.return_value = [
            {"description": "Add more tests", "priority": "High"}
        ]
        result = self.repo.generate_future_suggestion(mock_llm)
        self.assertIsInstance(result, list)
        self.assertEqual(result[0]["description"], "Add more tests")
        self.assertEqual(result[0]["priority"], "High")
        mock_generate_suggestion.assert_called_once()

if __name__ == "__main__":
    unittest.main()
