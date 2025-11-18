import unittest
from function import generate_future_suggestion

class DummyLLM:
    def generate(self, prompt):
        return "future suggestion"

def dummy_build_future_prompt(requirements, commit_history, code_summary):
    return f"PROMPT:{requirements}:{commit_history}:{code_summary}"

def patch_prompt():
    import sys
    sys.modules["prompt.future_suggestion_prompt"] = type("mod", (), {
        "build_future_prompt": dummy_build_future_prompt
    })
    sys.modules["llm.base"] = type("mod", (), {
        "LLMBase": DummyLLM
    })

class TestGenerateFutureSuggestion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch_prompt()

    def test_generate_future_suggestion(self):
        llm = DummyLLM()
        requirements = "Add login"
        commit_history = ["init", "add user"]
        code_summary = [("main.py", "file", "desc")]
        suggestion = generate_future_suggestion.generate_future_suggestion(
            requirements, commit_history, code_summary, llm
        )
        self.assertEqual(suggestion, "future suggestion")

if __name__ == "__main__":
    unittest.main()
