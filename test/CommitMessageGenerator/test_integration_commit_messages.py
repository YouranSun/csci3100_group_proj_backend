import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestIntegrationCommitMessages(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for integration testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.LLMBase")
    @patch("Repository.repository.generate_commit_message")
    @patch("Repository.repository.CommitsDB")
    def test_generate_commit_messages_for_grouped_changes(self, MockCommitsDB, mock_generate_commit_message, MockLLMBase):
        """
        Integration test: generate commit messages for grouped changes using mock LLM.
        """
        mock_db = MagicMock()
        MockCommitsDB.return_value = mock_db
        mock_llm = MockLLMBase()
        mock_generate_commit_message.return_value = "Refactor code"
        mock_db.get_diffs_in_group.return_value = ["diff1", "diff2"]
        mock_db.get_diff.side_effect = [{"id": "diff1"}, {"id": "diff2"}]
        group_id = "group1"
        try:
            self.repo.generate_group_commit_message(mock_llm, group_id)
        except Exception as e:
            self.fail(f"Generate commit messages for grouped changes raised an exception: {e}")
        mock_generate_commit_message.assert_called_once()
        # Assert that generate_commit_message was called with correct arguments
        mock_generate_commit_message.assert_called_with(mock_llm, [{'id': 'diff1'}, {'id': 'diff2'}])
        mock_db.modify_commit_message.assert_called_once_with(group_id, "Refactor code")
        # mock_db.close.assert_called()

if __name__ == "__main__":
    unittest.main()
