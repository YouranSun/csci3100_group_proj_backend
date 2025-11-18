import unittest
from prompt import split_commit_prompt

class TestSplitCommitPrompt(unittest.TestCase):
    def test_build_atomic_split_prompt(self):
        diff_summary = "diff block content"
        prompt = split_commit_prompt.build_atomic_split_prompt(diff_summary)
        self.assertIn("You are a senior software engineer", prompt)
        self.assertIn("Output JSON format strictly as:", prompt)
        self.assertIn(diff_summary, prompt)
        self.assertIn("Return only the JSON result", prompt)
        self.assertIn("split_lines", prompt)

if __name__ == "__main__":
    unittest.main()
