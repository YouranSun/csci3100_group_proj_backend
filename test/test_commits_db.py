import unittest
import tempfile
import shutil
from pathlib import Path
from db.commits_db import CommitsDB

class TestCommitsDB(unittest.TestCase):
    def setUp(self):
        # 创建临时目录，避免污染真实数据
        self.temp_dir = tempfile.mkdtemp()
        self.git_path = self.temp_dir
        self.db = CommitsDB(git_path=self.git_path, base_dir=Path(self.temp_dir))

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.temp_dir)

    def test_create_and_list_commit_group(self):
        self.db.create_commit_group("g1", "group1")
        groups = self.db.list_commit_groups()
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["id"], "g1")
        self.assertEqual(groups[0]["name"], "group1")

    def test_rename_commit_group(self):
        self.db.create_commit_group("g2", "oldname")
        self.db.rename_commit_group("g2", "newname")
        group = self.db.get_commit_group("g2")
        self.assertEqual(group["name"], "newname")

    def test_delete_commit_group(self):
        self.db.create_commit_group("g3", "group3")
        self.db.delete_commit_group("g3")
        group = self.db.get_commit_group("g3")
        self.assertIsNone(group)

    def test_add_and_get_atomic_diff(self):
        self.db.add_atomic_diff("d1", "file.py", True, False, 1, 2, ["a"], ["b"])
        diff = self.db.get_diff("d1")
        self.assertEqual(diff["file_path"], "file.py")
        self.assertEqual(diff["is_new_file"], True)
        self.assertEqual(diff["old_lines"], ["a"])
        self.assertEqual(diff["new_lines"], ["b"])

    def test_set_group_diffs(self):
        self.db.create_commit_group("g4", "group4")
        self.db.add_atomic_diff("d2", "file2.py", False, False, 3, 4, ["x"], ["y"])
        self.db.set_group_diffs("g4", ["d2"])
        diffs = self.db.get_diffs_in_group("g4")
        self.assertEqual(diffs, ["d2"])

    def test_commit_message(self):
        self.db.create_commit_group("g5", "group5")
        self.db.modify_commit_message("g5", "msg")
        msg = self.db.get_commit_message("g5")
        self.assertEqual(msg, "msg")

    def test_metadata_hash(self):
        self.db.set_last_index_hash("hash123")
        hash_val = self.db.get_last_index_hash()
        self.assertEqual(hash_val, "hash123")

    def test_clear_all_groups(self):
        self.db.create_commit_group("g6", "group6")
        self.db.clear_all_groups()
        groups = self.db.list_commit_groups()
        self.assertEqual(groups, [])

    def test_clear_all_atomic_diffs(self):
        self.db.add_atomic_diff("d3", "file3.py", False, True, 5, 6, ["old"], ["new"])
        self.db.clear_all_atomic_diffs()
        diff = self.db.get_diff("d3")
        self.assertIsNone(diff)

if __name__ == "__main__":
    unittest.main()
