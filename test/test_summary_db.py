import unittest
import tempfile
import shutil
from pathlib import Path
from db.summary_db import SummaryDB

class TestSummaryDB(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.git_path = self.temp_dir
        self.db = SummaryDB(git_path=self.git_path, base_dir=self.temp_dir)

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.temp_dir)

    def test_save_and_get_node(self):
        self.db.save_node("file1.py", "file", "summary1")
        node = self.db.get_node("file1.py")
        self.assertIsNotNone(node)
        self.assertEqual(node[0], "file")
        self.assertEqual(node[1], "summary1")

    def test_list_nodes(self):
        self.db.save_node("file2.py", "file", "summary2")
        self.db.save_node("file3.py", "file", "summary3")
        nodes = self.db.list_nodes()
        paths = [n[0] for n in nodes]
        self.assertIn("file2.py", paths)
        self.assertIn("file3.py", paths)

    def test_clear_all_nodes(self):
        self.db.save_node("file4.py", "file", "summary4")
        self.db.clear_all_nodes()
        nodes = self.db.list_nodes()
        self.assertEqual(nodes, [])

if __name__ == "__main__":
    unittest.main()
