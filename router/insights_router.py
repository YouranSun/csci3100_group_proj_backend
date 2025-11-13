# router/insights_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from llm.openai_llm import OpenAILLM
from repository import Repository

from function.generate_future_suggestion import generate_future_suggestion

router = APIRouter()

class FutureSuggestionsRequest(BaseModel):
    repo_path: str
    requirements: str = ""
    max_commits: int = 50

@router.post("/insights")
def generate_future_suggestions(req: FutureSuggestionsRequest):
    print("entered")
    try:
        repo = Repository(req.repo_path)
        commit_history = repo.get_commit_messages(limit=req.max_commits)
        code_summary = repo.get_summary()
        llm = OpenAILLM(model="gpt-4o-mini")

        insights = generate_future_suggestion(req.requirements, commit_history, code_summary, llm)

        return insights

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
