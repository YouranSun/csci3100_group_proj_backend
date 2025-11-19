import unittest
import tempfile
import os
from pathlib import Path
from Repository.diff import Hunk, AtomicDiff

class TestAtomicDiff(unittest.TestCase):
    def test_to_dict_and_build_from_dict(self):
        hunk = Hunk(1, 1, ["a"], ["b"])
        diff = AtomicDiff(file_path="foo.txt", is_new_file=False, is_deleted_file=False, hunk=hunk)
        d = diff.to_dict()
        self.assertEqual(d["file_path"], "foo.txt")
        self.assertEqual(d["old_lines"], ["a"])
        self.assertEqual(d["new_lines"], ["b"])

        diff2 = AtomicDiff()
        diff2.build_from_dict(d)
        self.assertEqual(diff2.file_path, "foo.txt")
        self.assertEqual(diff2.hunk.old_lines, ["a"])
        self.assertEqual(diff2.hunk.new_lines, ["b"])

    def test_apply_new_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            hunk = Hunk(1, 1, [], ["hello", "world"])
            diff = AtomicDiff(file_path="bar.txt", is_new_file=True, hunk=hunk)
            diff.apply(repo_root)
            content = (repo_root / "bar.txt").read_text()
            self.assertEqual(content, "hello\nworld")

    def test_apply_deleted_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            file_path = repo_root / "baz.txt"
            file_path.write_text("abc")
            hunk = Hunk(1, 1, ["abc"], [])
            diff = AtomicDiff(file_path="baz.txt", is_deleted_file=True, hunk=hunk)
            diff.apply(repo_root)
            self.assertFalse(file_path.exists())

    def test_apply_modify(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            file_path = repo_root / "mod.txt"
            file_path.write_text("foo\nbar\nbaz")
            hunk = Hunk(2, 2, ["bar"], ["BAR"])
            diff = AtomicDiff(file_path="mod.txt", hunk=hunk)
            diff.apply(repo_root)
            content = file_path.read_text()
            self.assertEqual(content, "foo\nBAR\nbaz")

    def test_apply_hunk_mismatch(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            file_path = repo_root / "fail.txt"
            file_path.write_text("foo\nbar\nbaz")
            hunk = Hunk(2, 2, ["xxx"], ["BAR"])
            diff = AtomicDiff(file_path="fail.txt", hunk=hunk)
            with self.assertRaises(ValueError):
                diff.apply(repo_root)

if __name__ == "__main__":
    unittest.main()
