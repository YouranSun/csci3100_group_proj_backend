from fastapi import APIRouter, Depends, HTTPException
from repository_manager import RepositoryManager
from db.summary_db import SummaryDB
from repository import Repository
from llm.openai_llm import OpenAILLM
from function.generate_summary import generate_repository_abstract, build_tree

from pathlib import Path
from collections import defaultdict

router = APIRouter()

# Dependency 注入
def get_repo_manager():
    from db.repo_db import RepoDB
    db = RepoDB()
    manager = RepositoryManager(db)
    try:
        yield manager
    finally:
        db.close()

# GET /abstract/{repo_path} 返回树形摘要
@router.get("/abstract")
def get_abstract(repo_path: str, manager: RepositoryManager = Depends(get_repo_manager)):
    print("Repo path:", repo_path)
    try:
        repo = manager.get_repository(repo_path)
        db = SummaryDB(repo.repo_path)
        nodes = db.list_nodes()
        print("Summary nodes:", nodes)
        db.close()

        if not nodes:
            return {"message": "Summary not generated yet", "tree": None}

        tree = build_tree(nodes)
        print("Tree: tree")
        return {"tree": tree}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# POST /abstract/{repo_path}/refresh 重新生成摘要
@router.post("/abstract/refresh")
def refresh_abstract(repo_path: str, manager: RepositoryManager = Depends(get_repo_manager)):
    try:
        repo = manager.get_repository(repo_path)

        llm = OpenAILLM(model="gpt-4o-mini")

        # 生成摘要并保存到数据库
        generate_repository_abstract(llm, repo)

        print("successfully generated")

        # 返回最新树
        db = SummaryDB(repo.repo_path)
        nodes = db.list_nodes()
        db.close()
        tree = build_tree(nodes)

        return {"tree": tree, "message": "Summary refreshed successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
