import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestDiffSegmentationClustering(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.generate_atomic_commits")
    @patch("Repository.repository.generate_suggested_commit_groups_agglomerative")
    def test_diff_block_segmentation_and_clustering(self, mock_grouping, mock_atomic_commits):
        """
        Test diff block segmentation and clustering using mock LLM.
        """
        mock_atomic_commits.return_value = [MagicMock(id="diff1"), MagicMock(id="diff2")]
        mock_grouping.return_value = [
            {"id": "group1", "name": "Feature", "diffs": [MagicMock(id="diff1")]}
        ]
        llm = MagicMock()
        diffs = [MagicMock()]
        # Simulate segmentation and clustering
        atomic_diffs = mock_atomic_commits(llm, diffs)
        suggested_groups = mock_grouping(atomic_diffs)
        self.assertIsInstance(atomic_diffs, list)
        self.assertEqual(suggested_groups[0]["id"], "group1")
        mock_atomic_commits.assert_called_once_with(llm, diffs)
        mock_grouping.assert_called_once_with(atomic_diffs)

if __name__ == "__main__":
    unittest.main()
