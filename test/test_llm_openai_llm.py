import unittest
from llm.openai_llm import OpenAILLM

class DummyChoices:
    def __init__(self, content):
        self.message = type("msg", (), {"content": content})

class DummyResp:
    def __init__(self, content):
        self.choices = [DummyChoices(content)]

class DummyChatCompletions:
    def create(self, model, messages, temperature, **kwargs):
        # 返回模拟响应
        return DummyResp("dummy response")

class DummyChat:
    def __init__(self):
        self.completions = DummyChatCompletions()

class DummyOpenAI:
    def __init__(self):
        self.chat = DummyChat()

def patch_openai():
    import sys
    sys.modules["openai"] = type("mod", (), {
        "OpenAI": DummyOpenAI
    })

class TestOpenAILLM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        patch_openai()

    def test_generate(self):
        llm = OpenAILLM(model="gpt-4o-mini", temperature=0.3)
        result = llm.generate("hello")
        self.assertEqual(result, "dummy response")

if __name__ == "__main__":
    unittest.main()
