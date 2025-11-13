import json
from llm.base import LLMBase
from typing import List, Tuple

from prompt.future_suggestion_prompt import build_future_prompt

def generate_future_suggestion(
    requirements: str,
    commit_history: list[str],
    code_summary: List[Tuple[str, str, str]], 
    llm: LLMBase,
):
    
    prompt = build_future_prompt(
        requirements=requirements,
        commit_history=commit_history,
        code_summary=code_summary
    )

    suggestion = llm.generate(prompt)

    return suggestion