import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestApplyGroupedChanges(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.AtomicDiff")
    def test_applying_grouped_changes_to_filesystem(self, MockAtomicDiff):
        """
        Test applying grouped changes to the filesystem using mock AtomicDiff.
        """
        mock_atomic = MockAtomicDiff()
        mock_atomic.apply.return_value = "applied"
        group = {"diff_ids": ["diff1", "diff2"]}
        diffs = {"diff1": mock_atomic, "diff2": mock_atomic}
        files = self.repo.apply_diff_group(group, diffs)
        self.assertIsInstance(files, list)
        # Assert that apply was called for each diff_id
        calls = [((self.repo.repo_path,),)] * len(group["diff_ids"])
        mock_atomic.apply.assert_has_calls(calls, any_order=True)

if __name__ == "__main__":
    unittest.main()
