import unittest
from prompt import summary_prompt

class TestSummaryPrompt(unittest.TestCase):
    def test_build_file_summary_prompt(self):
        file_name = "foo.py"
        file_content = "def f(): pass"
        prompt = summary_prompt.build_file_summary_prompt(file_name, file_content)
        self.assertIn("You are an assistant that summarizes source code files.", prompt)
        self.assertIn(file_name, prompt)
        self.assertIn(file_content, prompt)
        self.assertIn("Return only the summary", prompt)

    def test_build_directory_summary_prompt(self):
        dir_name = "utils"
        child_summaries = "foo.py: does X"
        prompt = summary_prompt.build_directory_summary_prompt(dir_name, child_summaries)
        self.assertIn("You are an assistant that summarizes a software module or directory.", prompt)
        self.assertIn(dir_name, prompt)
        self.assertIn(child_summaries, prompt)
        self.assertIn("Return only the summary", prompt)

if __name__ == "__main__":
    unittest.main()
