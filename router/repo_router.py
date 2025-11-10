# routers/repo_router.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from repository_manager import RepositoryManager
from db.repo_db import RepoDB

router = APIRouter()

class AddRepoRequest(BaseModel):
    path: str
    name: Optional[str] = None

# Dependency
def get_repo_manager():
    db = RepoDB()
    manager = RepositoryManager(db)
    try:
        yield manager
    finally:
        db.close()

# GET /repos
@router.get("/repos")
def list_repos(manager: RepositoryManager = Depends(get_repo_manager)):
    return [r.to_dict() for r in manager.list_repositories()]

# POST /repos
@router.post("/repos")
def add_repo(req: AddRepoRequest, manager: RepositoryManager = Depends(get_repo_manager)):
    print(req)
    try:
        repo_info = manager.add_repository(req.path, req.name)
        print(repo_info)
        return repo_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
