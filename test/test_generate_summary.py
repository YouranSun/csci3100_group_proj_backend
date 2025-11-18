import unittest
from function import generate_summary

class DummyLLM:
    def generate(self, prompt):
        return f"summary:{prompt}"

def dummy_build_file_summary_prompt(name, content):
    return f"FILE_PROMPT:{name}:{content}"

def dummy_build_directory_summary_prompt(name, merged_text):
    return f"DIR_PROMPT:{name}:{merged_text}"

class DummyDB:
    def __init__(self, repo_path):
        self.nodes = []
    def save_node(self, rel_path, node_type, summary):
        self.nodes.append((rel_path, node_type, summary))
    def clear_all_nodes(self):
        self.nodes.clear()
    def list_nodes(self):
        return self.nodes
    def close(self):
        pass

def patch_deps():
    import sys
    sys.modules["llm.base"] = type("mod", (), {
        "LLMBase": DummyLLM
    })
    sys.modules["prompt.summary_prompt"] = type("mod", (), {
        "build_file_summary_prompt": dummy_build_file_summary_prompt,
        "build_directory_summary_prompt": dummy_build_directory_summary_prompt
    })
    sys.modules["db.summary_db"] = type("mod", (), {
        "SummaryDB": DummyDB
    })
    sys.modules["Repository.repository"] = type("mod", (), {
        "repository": object
    })

class TestGenerateSummary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch_deps()

    def test_summarize_file(self):
        llm = DummyLLM()
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "a.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("hello world")
            rel_path, summary = generate_summary.summarize_file(llm, file_path, tmpdir)
            self.assertIn("summary:FILE_PROMPT:a.txt:hello world", summary)

    def test_build_tree(self):
        nodes = [
            ("a.txt", "file", "summary a"),
            ("dir1/b.txt", "file", "summary b"),
            ("dir1", "dir", "summary dir1"),
            (".", "dir", "summary root")
        ]
        tree = generate_summary.build_tree(nodes)
        self.assertEqual(tree[0]["name"], ".")
        self.assertEqual(tree[0]["type"], "dir")
        self.assertEqual(tree[0]["summary"], "summary root")
        self.assertTrue(any(child["name"] == "dir1" for child in tree[0]["children"]))

if __name__ == "__main__":
    unittest.main()
