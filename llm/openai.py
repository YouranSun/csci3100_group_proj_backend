# llm/openai_llm.py
from openai import OpenAI
from .base import LLMBase

class OpenAILLM(LLMBase):
    def __init__(self, model="gpt-4o-mini", temperature=0.3):
        super().__init__(model, temperature)
        self.client = OpenAI()

    def generate(self, prompt: str, **kwargs) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            **kwargs
        )
        return resp.choices[0].message.content.strip()
