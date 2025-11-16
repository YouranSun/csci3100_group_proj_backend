# router/commit_message_router.py
from fastapi import APIRouter
from router.router_request import CommitMessageRequest, EditCommitMessageRequest
from Repository.repository import Repository
from llm.openai_llm import OpenAILLM

router = APIRouter()


@router.post("/commit_message/generate")
def generate_group_commit_message(req: CommitMessageRequest):
    repo = Repository(req.repo_path)
    llm = OpenAILLM(model="gpt-4o-mini")
    repo.generate_group_commit_message(llm, req.group_id)
    message = repo.get_commit_message(req.group_id)
    return {"group_id": req.group_id, "message": message}


@router.post("/commit_message")
def get_commit_message(req: CommitMessageRequest):
    repo = Repository(req.repo_path)
    row = repo.get_commit_message(req.group_id)
    if row:
        return {"group_id": req.group_id, "message": row[0]}
    return {"group_id": req.group_id, "message": ""}


@router.post("/commit_message/edit")
def edit_commit_message(req: EditCommitMessageRequest):
    repo = Repository(req.repo_path)
    repo.modify_commit_message(req.group_id, req.message)
    return {"group_id": req.group_id, "message": req.message}
