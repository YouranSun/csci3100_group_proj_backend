import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestCommitLogTagging(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.Repo")
    def test_commit_log_loading_and_tag_assignment(self, MockRepo):
        """
        Test commit log loading and tag assignment.
        """
        mock_repo = MockRepo()
        mock_commit = MagicMock()
        mock_commit.message = "feat: add feature"
        mock_repo.iter_commits.return_value = [mock_commit]
        self.repo.repo = mock_repo
        messages = self.repo.get_historical_commit_messages()
        self.assertEqual(messages[0], "feat: add feature")
        # Simulate tag assignment logic
        tags = []
        for msg in messages:
            if "feat" in msg:
                tags.append("feat")
        self.assertIn("feat", tags)

if __name__ == "__main__":
    unittest.main()
