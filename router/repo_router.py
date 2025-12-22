# routers/repo_router.py
from fastapi import APIRouter, Depends, HTTPException
from Repository.repository_manager import RepositoryManager
from db.repo_db import RepoDB
from router.router_request import AddRepoRequest

router = APIRouter()



def get_repo_manager():
    db = RepoDB()
    manager = RepositoryManager(db)
    try:
        yield manager
    finally:
        db.close()



@router.get("/repos")
def list_repos(manager: RepositoryManager = Depends(get_repo_manager)):
    return [r for r in manager.list_repositories()]



@router.post("/repos")
def add_repo(req: AddRepoRequest, manager: RepositoryManager = Depends(get_repo_manager)):
    print(req)
    try:
        repo_info = manager.add_repository(req.repo_path, None)
        return repo_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
