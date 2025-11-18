import unittest
from function import generate_suggested_commit_groups

class DummyHunk:
    def __init__(self, old_lines, new_lines):
        self.old_lines = old_lines
        self.new_lines = new_lines

class DummyAtomicDiff:
    def __init__(self, file_path, hunk):
        self.file_path = file_path
        self.hunk = hunk

class DummyModel:
    def encode(self, texts, show_progress_bar=False):
        # 返回固定向量，模拟聚类
        return [[1, 0], [0, 1]]

def patch_sentence_transformer():
    import sys
    sys.modules["sentence_transformers"] = type("mod", (), {
        "SentenceTransformer": lambda name: DummyModel()
    })

class TestGenerateSuggestedCommitGroups(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch_sentence_transformer()

    def test_generate_suggested_commit_groups_agglomerative(self):
        d1 = DummyAtomicDiff("foo.py", DummyHunk(["a"], ["b"]))
        d2 = DummyAtomicDiff("bar.py", DummyHunk(["x"], ["y"]))
        groups = generate_suggested_commit_groups.generate_suggested_commit_groups_agglomerative([d1, d2], similarity_threshold=0.5)
        self.assertTrue(len(groups) >= 1)
        self.assertIn("id", groups[0])
        self.assertIn("name", groups[0])
        self.assertIn("diffs", groups[0])

if __name__ == "__main__":
    unittest.main()
