import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestDiffExtraction(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.parse_diff_blocks")
    def test_diff_extraction_from_working_tree(self, mock_parse_diff_blocks):
        """
        Test diff extraction from the working tree.
        """
        mock_parse_diff_blocks.return_value = [
            MagicMock(file_path="main.py", is_new_file=False, is_deleted_file=False)
        ]
        # self.repo.repo.git.diff = MagicMock(return_value="fake diff text")
        diffs = self.repo.diff_with_head()
        self.assertIsInstance(diffs, list)
        self.assertEqual(diffs[0].file_path, "main.py")
        mock_parse_diff_blocks.assert_called_once()

if __name__ == "__main__":
    unittest.main()
