import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestIntegrationSplitGroup(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for integration testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.LLMBase")
    def test_split_and_group_commits(self, MockLLMBase):
        """
        Integration test: split and group commits in test/example repo using mock LLM.
        """
        mock_llm = MockLLMBase()
        try:
            self.repo.generate_commit_groups(mock_llm)
        except Exception as e:
            self.fail(f"Split and group commits raised an exception: {e}")

if __name__ == "__main__":
    unittest.main()
