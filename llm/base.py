# llm/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMBase(ABC):
    """统一的 LLM 调用接口"""

    def __init__(self, model: str, temperature: float = 0.3):
        self.model = model
        self.temperature = temperature

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """主接口：输入prompt，返回生成文本"""
        pass

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """可选接口：支持chat格式"""
        # 默认退化为直接拼接messages
        prompt = "\n".join([m["content"] for m in messages])
        return self.generate(prompt, **kwargs)
