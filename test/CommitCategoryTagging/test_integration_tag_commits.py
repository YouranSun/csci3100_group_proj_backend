import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestIntegrationTagCommits(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for integration testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.Repo")
    def test_tag_commits_integration(self, MockRepo):
        """
        Integration test: tag commits in test/example repo using mock logic.
        """
        mock_repo = MockRepo()
        mock_commit1 = MagicMock()
        mock_commit1.message = "fix: bug fix"
        mock_commit2 = MagicMock()
        mock_commit2.message = "docs: update docs"
        mock_repo.iter_commits.return_value = [mock_commit1, mock_commit2]
        self.repo.repo = mock_repo
        messages = self.repo.get_historical_commit_messages()
        tags = []
        for msg in messages:
            if "fix" in msg:
                tags.append("fix")
            if "docs" in msg:
                tags.append("docs")
        self.assertIn("fix", tags)
        self.assertIn("docs", tags)

if __name__ == "__main__":
    unittest.main()
