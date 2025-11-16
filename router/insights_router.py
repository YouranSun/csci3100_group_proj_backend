# router/insights_router.py
from fastapi import APIRouter, HTTPException
from llm.openai_llm import OpenAILLM
from Repository.repository import Repository

from router.router_request import FutureSuggestionsRequest

router = APIRouter()


@router.post("/insights")
def generate_future_suggestions(req: FutureSuggestionsRequest):
    print("entered")
    repo = Repository(req.repo_path)
    llm = OpenAILLM(model="gpt-4o-mini")

    insights = repo.generate_future_suggestion(llm, req.requirements, req.max_commits)
    return insights