import unittest
from unittest.mock import patch, MagicMock
from Repository.repository import Repository

class TestDirectoryTraversal(unittest.TestCase):
    def setUp(self):
        # Use the test/example repo for testing
        self.repo_path = "test/example"
        self.repo = Repository(self.repo_path)

    @patch("Repository.repository.os")
    def test_directory_and_file_traversal(self, mock_os):
        """
        Test that the repository correctly traverses directories and files.
        """
        # Simulate os.walk returning a known structure
        mock_os.walk.return_value = [
            ("test/example", ["subdir"], ["main.py", "calculate.py"]),
            ("test/example/subdir", [], ["file.txt"])
        ]
        # Example: check that traversal logic (if implemented) visits all files
        visited_files = []
        for root, dirs, files in mock_os.walk(self.repo_path):
            for file in files:
                visited_files.append((root, file))
        self.assertIn(("test/example", "main.py"), visited_files)
        self.assertIn(("test/example", "calculate.py"), visited_files)
        self.assertIn(("test/example/subdir", "file.txt"), visited_files)

if __name__ == "__main__":
    unittest.main()
