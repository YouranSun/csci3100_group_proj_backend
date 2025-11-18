import unittest
from function import generate_atomic_commits

class DummyLLM:
    def generate(self, prompt):
        # 返回固定的拆分建议
        return '{"splits":[{"file":"foo.py","split_lines":[1]}]}'

class DummyHunk:
    def __init__(self, old_start, new_start, old_lines, new_lines):
        self.old_start = old_start
        self.new_start = new_start
        self.old_lines = old_lines
        self.new_lines = new_lines

class DummyAtomicDiff:
    def __init__(self, file_path, is_new_file, is_deleted_file, hunk):
        self.file_path = file_path
        self.is_new_file = is_new_file
        self.is_deleted_file = is_deleted_file
        self.hunk = hunk
    def to_dict(self):
        return {
            "file_path": self.file_path,
            "is_new_file": self.is_new_file,
            "is_deleted_file": self.is_deleted_file,
            "hunk": {
                "old_start": self.hunk.old_start,
                "new_start": self.hunk.new_start,
                "old_lines": self.hunk.old_lines,
                "new_lines": self.hunk.new_lines,
            }
        }

def patch_atomicdiff():
    import sys
    sys.modules["Repository.diff"] = type("mod", (), {
        "AtomicDiff": DummyAtomicDiff,
        "Hunk": DummyHunk
    })
    sys.modules["llm.base"] = type("mod", (), {
        "LLMBase": DummyLLM
    })
    sys.modules["prompt.split_commit_prompt"] = type("mod", (), {
        "build_atomic_split_prompt": lambda d: "prompt"
    })

class TestGenerateAtomicCommits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch_atomicdiff()

    def test_suggest_commit_splits(self):
        llm = DummyLLM()
        diff = DummyAtomicDiff("foo.py", True, False, DummyHunk(0, 1, [], ["a", "b"]))
        result = generate_atomic_commits.suggest_commit_splits(llm, [diff])
        self.assertIn("splits", result)
        self.assertEqual(result["splits"][0]["file"], "foo.py")

    def test_apply_split_suggestions(self):
        diff = DummyAtomicDiff("foo.py", True, False, DummyHunk(0, 1, [], ["a", "b"]))
        split_result = {"splits": [{"file": "foo.py", "split_lines": [1]}]}
        new_diffs = generate_atomic_commits.apply_split_suggestions([diff], split_result)
        self.assertEqual(len(new_diffs), 2)
        self.assertEqual(new_diffs[0].hunk.new_lines, ["a"])
        self.assertEqual(new_diffs[1].hunk.new_lines, ["b"])

    def test_generate_atomic_commits(self):
        llm = DummyLLM()
        diff = DummyAtomicDiff("foo.py", True, False, DummyHunk(0, 1, [], ["a", "b"]))
        atomic_diffs = generate_atomic_commits.generate_atomic_commits(llm, [diff])
        self.assertEqual(len(atomic_diffs), 2)
        self.assertEqual(atomic_diffs[0].hunk.new_lines, ["a"])
        self.assertEqual(atomic_diffs[1].hunk.new_lines, ["b"])

if __name__ == "__main__":
    unittest.main()
