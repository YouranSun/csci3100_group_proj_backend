import unittest
from prompt import future_suggestion_prompt

class TestFutureSuggestionPrompt(unittest.TestCase):
    def test_build_future_prompt(self):
        requirements = "Improve performance"
        commit_history = ["init", "add feature"]
        code_summary = [("main.py", "file", "desc")]
        prompt = future_suggestion_prompt.build_future_prompt(requirements, commit_history, code_summary)
        self.assertIn("Improve performance", prompt)
        self.assertIn("- add feature", prompt)
        self.assertIn("[file] main.py: desc", prompt)
        self.assertIn("Return **only valid JSON**", prompt)
        self.assertIn("priority", prompt)
        self.assertIn("category", prompt)

if __name__ == "__main__":
    unittest.main()
