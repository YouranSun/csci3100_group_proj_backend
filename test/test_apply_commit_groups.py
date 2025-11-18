import unittest
from function import apply_commit_groups

class DummyHunk:
    def __init__(self, old_start, new_start, old_lines, new_lines):
        self.old_start = old_start
        self.new_start = new_start
        self.old_lines = old_lines
        self.new_lines = new_lines
        self.file_path = None

class DummyAtomicDiff:
    def __init__(self, file_path, is_new_file, is_deleted_file, hunk):
        self.file_path = file_path
        self.is_new_file = is_new_file
        self.is_deleted_file = is_deleted_file
        self.hunk = hunk

def patch_atomicdiff():
    import sys
    sys.modules["Repository.diff"] = type("mod", (), {
        "AtomicDiff": DummyAtomicDiff,
        "Hunk": DummyHunk
    })

class TestApplyCommitGroups(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch_atomicdiff()

    def test_parse_diff_blocks_basic(self):
        diff_text = (
            "diff --git a/foo.py b/foo.py\n"
            "new file mode 100644\n"
            "@@ -0,0 +1,2 @@\n"
            "+print('hello')\n"
            "+print('world')\n"
        )
        results = apply_commit_groups.parse_diff_blocks(diff_text)
        self.assertEqual(len(results), 1)
        diff = results[0]
        self.assertEqual(diff.file_path, "foo.py")
        self.assertTrue(diff.is_new_file)
        self.assertFalse(diff.is_deleted_file)
        self.assertEqual(diff.hunk.old_start, 0)
        self.assertEqual(diff.hunk.new_start, 1)
        self.assertEqual(diff.hunk.old_lines, [])
        self.assertEqual(diff.hunk.new_lines, ["print('hello')", "print('world')"])

    def test_adjust_later_groups(self):
        # 构造 groups 和 diffs
        h1 = DummyHunk(1, 1, ["a"], ["a", "b"])
        h2 = DummyHunk(3, 3, ["x"], ["x"])
        d1 = DummyAtomicDiff("f.py", False, False, h1)
        d2 = DummyAtomicDiff("f.py", False, False, h2)
        diffs = {"d1": d1, "d2": d2}
        groups = [
            {"diff_ids": ["d1"]},
            {"diff_ids": ["d2"]}
        ]
        apply_commit_groups.adjust_later_groups(groups, diffs, 0)
        self.assertEqual(d2.hunk.old_start, 4)  # 原为3，被+1

    def test_adjust_later_diffs(self):
        h1 = DummyHunk(1, 1, ["a"], ["a", "b"])
        h2 = DummyHunk(3, 3, ["x"], ["x"])
        d1 = DummyAtomicDiff("f.py", False, False, h1)
        d2 = DummyAtomicDiff("f.py", False, False, h2)
        diffs = {"d1": d1, "d2": d2}
        group = {"diff_ids": ["d1", "d2"]}
        apply_commit_groups.adjust_later_diffs(group, diffs, 0)
        self.assertEqual(d2.hunk.old_start, 4)

if __name__ == "__main__":
    unittest.main()
