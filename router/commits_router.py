# commits_router.py
from fastapi import APIRouter, HTTPException

from Repository.repository import Repository
from llm.openai_llm import OpenAILLM

from router.router_request import GetCommitGroupsRequest, CommitGroupRequest, DeleteGroupRequest, ApplyCommitGroupsRequest, ReorderGroupsRequest, MoveDiffRequest, GetAtomicDiffsRequest

router = APIRouter()


@router.post("/commit_groups")
def get_commit_groups(
    req: GetCommitGroupsRequest,
):
    llm = OpenAILLM(model="gpt-4o-mini")
    repo = Repository(req.repo_path)
    repo.generate_commit_groups(llm)
    groups = repo.list_commit_groups()
    return {"groups": groups}



@router.post("/commit_groups/move_diff")
def move_diff(req: MoveDiffRequest):
    repo = Repository(req.repo_path)
    repo.move_diff_to_group(req.diff_id, req.target_group_id)
    return {"status": "ok"}



@router.post("/commit_groups")
def create_commit_group(req: CommitGroupRequest):
    repo = Repository(req.repo_path)
    repo.create_commit_group(req.group_id, req.name)
    return {"id": req.group_id, "name": req.name}



@router.delete("/commit_groups/delete")
def delete_commit_group(req: DeleteGroupRequest):
    repo = Repository(req.repo_path)
    group = repo.get_commit_group(req.group_id)
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group["diff_ids"]:
        raise HTTPException(status_code=400, detail="Cannot delete non-empty group")

    repo.delete_commit_group(req.group_id)
    return {"status": "ok"}



@router.post("/commit_groups/reorder")
def reorder_groups(req: ReorderGroupsRequest):
    repo = Repository(req.repo_path)
    repo.reorder_groups(req.ordered_ids)
    return {"status": "ok"}



@router.post("/atomic_diffs")
def get_atomic_diffs(req: GetAtomicDiffsRequest):
    repo = Repository(req.repo_path)
    diff_details = repo.list_atomic_diffs()
    return {"diffDetails": diff_details}



@router.post("/commit_groups/apply")
async def commit_groups(req: ApplyCommitGroupsRequest):
    repo = Repository(req.repo_path)
    result = repo.apply_commit_groups()

    return {"status": "ok", "result": result}