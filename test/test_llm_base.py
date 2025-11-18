import unittest
from llm.base import LLMBase

class DummyLLMBase(LLMBase):
    def __init__(self, model="dummy", temperature=0.3):
        super().__init__(model, temperature)
        self.last_prompt = None
    def generate(self, prompt: str, **kwargs) -> str:
        self.last_prompt = prompt
        return f"GEN:{prompt}"

class TestLLMBase(unittest.TestCase):
    def test_generate(self):
        llm = DummyLLMBase()
        result = llm.generate("hello")
        self.assertEqual(result, "GEN:hello")
        self.assertEqual(llm.last_prompt, "hello")

    def test_chat(self):
        llm = DummyLLMBase()
        messages = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"}
        ]
        result = llm.chat(messages)
        self.assertEqual(result, "GEN:hi\nhello")
        self.assertEqual(llm.last_prompt, "hi\nhello")

if __name__ == "__main__":
    unittest.main()
