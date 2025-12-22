import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestCommitMessageGeneration(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.LLMBase")
    @patch("Repository.repository.generate_commit_message")
    @patch("Repository.repository.CommitsDB")
    def test_commit_message_generation(self, MockCommitsDB, mock_generate_commit_message, MockLLMBase):
        """
        Test commit message generation using mock LLM.
        """
        mock_db = MagicMock()
        MockCommitsDB.return_value = mock_db
        mock_llm = MockLLMBase()
        mock_generate_commit_message.return_value = "Add new feature"
        mock_db.get_diffs_in_group.return_value = ["diff1"]
        mock_db.get_diff.return_value = {"id": "diff1"}
        group_id = "group1"
        # Should call generate_commit_message and modify_commit_message
        self.repo.generate_group_commit_message(mock_llm, group_id)
        mock_generate_commit_message.assert_called_once()
        mock_generate_commit_message.assert_called_with(mock_llm, [{'id': 'diff1'}])
        mock_db.modify_commit_message.assert_called_once_with(group_id, "Add new feature")
        # mock_db.close.assert_called()

if __name__ == "__main__":
    unittest.main()
