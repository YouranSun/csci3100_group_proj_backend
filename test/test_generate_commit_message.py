import unittest
from function import generate_commit_message

class DummyLLM:
    def generate(self, prompt):
        return "commit message"

def dummy_build_commit_prompt(diff_summary):
    return f"PROMPT:{diff_summary}"

def patch_prompt():
    import sys
    sys.modules["prompt.commit_message_prompt"] = type("mod", (), {
        "build_commit_prompt": dummy_build_commit_prompt
    })
    sys.modules["llm.base"] = type("mod", (), {
        "LLMBase": DummyLLM
    })

class TestGenerateCommitMessage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch_prompt()

    def test_summarize_diff(self):
        diff_dicts = [
            {
                "file_path": "foo.py",
                "is_new_file": True,
                "is_deleted_file": False,
                "old_lines": [],
                "new_lines": ["a", "b"]
            },
            {
                "file_path": "bar.py",
                "is_new_file": False,
                "is_deleted_file": True,
                "old_lines": ["x"],
                "new_lines": []
            }
        ]
        summary = generate_commit_message.summarize_diff(diff_dicts)
        self.assertIn("File: foo.py", summary)
        self.assertIn("Added:", summary)
        self.assertIn("+ a", summary)
        self.assertIn("File: bar.py", summary)
        self.assertIn("Removed:", summary)
        self.assertIn("- x", summary)

    def test_generate_commit_message(self):
        llm = DummyLLM()
        diff_dicts = [
            {
                "file_path": "foo.py",
                "is_new_file": True,
                "is_deleted_file": False,
                "old_lines": [],
                "new_lines": ["a", "b"]
            }
        ]
        msg = generate_commit_message.generate_commit_message(llm, diff_dicts)
        self.assertEqual(msg, "commit message")

if __name__ == "__main__":
    unittest.main()
