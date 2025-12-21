import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestIntegrationExecuteCommits(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for integration testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.Repository.reset_to_head")
    @patch("Repository.repository.Repository.apply_diff_group")
    @patch("Repository.repository.Repository.stage_files")
    @patch("Repository.repository.Repository.commit")
    @patch("Repository.repository.Repository.list_commit_groups")
    @patch("Repository.repository.Repository.get_atomic_diffs")
    @patch("Repository.repository.Repository.get_commit_message")
    def test_execute_grouped_commits(self, mock_get_commit_message, mock_get_atomic_diffs, mock_list_commit_groups, mock_commit, mock_stage_files, mock_apply_diff_group, mock_reset_to_head):
        """
        Integration test: execute grouped commits in test/example repo using mocks.
        """
        mock_list_commit_groups.return_value = [
            {"id": "group1", "diff_ids": ["diff1"]},
            {"id": "group2", "diff_ids": ["diff2"]}
        ]
        mock_get_atomic_diffs.return_value = {"diff1": MagicMock(), "diff2": MagicMock()}
        mock_get_commit_message.side_effect = ["Message 1", "Message 2"]
        mock_apply_diff_group.return_value = ["file1.py"]
        try:
            applied = self.repo.apply_commit_groups()
            self.assertIsInstance(applied, list)
            self.assertEqual(len(applied), 2)
        except Exception as e:
            self.fail(f"Execute grouped commits raised an exception: {e}")
        mock_reset_to_head.assert_called_once()
        # Assert that apply_diff_group was called with correct arguments
        expected_calls = [
            (({'id': 'group1', 'diff_ids': ['diff1']}, {'diff1': mock_get_atomic_diffs.return_value['diff1'], 'diff2': mock_get_atomic_diffs.return_value['diff2']}),),
            (({'id': 'group2', 'diff_ids': ['diff2']}, {'diff1': mock_get_atomic_diffs.return_value['diff1'], 'diff2': mock_get_atomic_diffs.return_value['diff2']}),)
        ]
        mock_apply_diff_group.assert_has_calls(expected_calls, any_order=False)
        mock_stage_files.assert_called()
        mock_commit.assert_called()

if __name__ == "__main__":
    unittest.main()
