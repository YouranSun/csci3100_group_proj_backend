import unittest
from Repository import repository

class DummyRepo:
    def __init__(self, path):
        self.path = path
        self.head = type("head", (), {"commit": type("commit", (), {"hexsha": "abc123"})})()
    def git(self):
        return self
    def diff(self, *args, **kwargs):
        return ""
    def iter_commits(self, *args, **kwargs):
        return []

class DummySummaryDB:
    def __init__(self, repo_path):
        self.repo_path = repo_path
    def list_nodes(self):
        return [("foo.py", "file", "desc")]
    def close(self):
        pass

class DummyCommitsDB:
    def __init__(self, repo_path):
        self.repo_path = repo_path
    def get_last_index_hash(self):
        return "dummy"
    def list_commit_groups(self):
        return [{"id": "g1", "name": "Group1", "diff_ids": []}]
    def list_atomic_diffs(self):
        return {}
    def clear_all_groups(self): pass
    def clear_all_atomic_diffs(self): pass
    def add_atomic_diff(self, **kwargs): pass
    def create_commit_group(self, group_id, name): pass
    def set_group_diffs(self, group_id, diff_ids): pass
    def set_last_index_hash(self, diff_hash): pass
    def get_commit_group(self, group_id): return {"id": group_id, "name": "Group"}
    def move_diff_to_group(self, diff_id, target_group_id): pass
    def delete_commit_group(self, group_id): pass
    def reorder_groups(self, ordered_ids): pass
    def get_diffs_in_group(self, group_id): return []
    def get_diff(self, diff_id): return None
    def modify_commit_message(self, group_id, message): pass
    def get_commit_message(self, group_id): return "msg"

class DummyLLMBase:
    def generate(self, prompt, **kwargs): return "summary"

def patch_deps():
    import sys
    sys.modules["git"] = type("mod", (), {"Repo": DummyRepo})
    sys.modules["db.summary_db"] = type("mod", (), {"SummaryDB": DummySummaryDB})
    sys.modules["db.commits_db"] = type("mod", (), {"CommitsDB": DummyCommitsDB})
    sys.modules["llm.base"] = type("mod", (), {"LLMBase": DummyLLMBase})

class TestRepository(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch_deps()

    def test_init_and_to_dict(self):
        repo = repository.Repository("test/example/repo")
        info = repo.to_dict()
        self.assertIn("path", info)
        self.assertIn("name", info)
        self.assertIn("last_commit", info)

    def test_get_summary(self):
        repo = repository.Repository("test/example/repo")
        nodes = repo.get_summary()
        self.assertTrue(nodes)
        self.assertEqual(nodes[0][0], "foo.py")

    def test_get_summary_tree(self):
        repo = repository.Repository("test/example/repo")
        tree = repo.get_summary_tree()
        self.assertTrue(tree)

    def test_list_commit_groups(self):
        repo = repository.Repository("test/example/repo")
        groups = repo.list_commit_groups()
        self.assertTrue(groups)
        self.assertEqual(groups[0]["id"], "g1")

if __name__ == "__main__":
    unittest.main()
