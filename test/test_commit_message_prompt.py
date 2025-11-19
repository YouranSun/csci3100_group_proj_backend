import unittest
from prompt import commit_message_prompt

class TestCommitMessagePrompt(unittest.TestCase):
    def test_build_commit_prompt(self):
        diff_summary = "Changed foo.py"
        prompt = commit_message_prompt.build_commit_prompt(diff_summary)
        self.assertIn("You are a helpful assistant", prompt)
        self.assertIn("Here is the diff summary:", prompt)
        self.assertIn(diff_summary, prompt)
        self.assertIn("Return only the commit message:", prompt)

if __name__ == "__main__":
    unittest.main()
