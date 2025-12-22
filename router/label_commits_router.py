from fastapi import APIRouter, HTTPException

from Repository.repository import Repository
from llm.openai_llm import OpenAILLM

from router.router_request import TagRequest

router = APIRouter()


@router.post("/labels")
def label_commits(req: TagRequest):
    llm = OpenAILLM(model="gpt-4o-mini")
    repo = Repository(req.repo_path)
    result = repo.label_commits(llm)
    print(result)
    return result
