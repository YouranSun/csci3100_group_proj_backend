from fastapi import APIRouter, HTTPException
from Repository.repository import Repository
from llm.openai_llm import OpenAILLM

from router.router_request import GetSummaryRequest, RefreshSummaryRequest

router = APIRouter()



@router.post("/summary")
def get_summary(req: GetSummaryRequest):
    print("Repo path:", req.repo_path)
    try:
        repo = Repository(req.repo_path)
        tree = repo.get_summary_tree()

        if not tree:
            return {"message": "Summary not generated yet", "tree": None}

        return {"tree": tree}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/summary/refresh")
def refresh_summary(req: RefreshSummaryRequest):
    repo = Repository(req.repo_path)

    llm = OpenAILLM(model="gpt-4o-mini")
    repo.generate_summary(llm)
    tree = repo.get_summary_tree()

    if not tree:
        return {"message": "Summary not generated yet", "tree": None}

    return {"tree": tree, "message": "Summary refreshed successfully"}
