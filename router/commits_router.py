# commits_router.py
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict
import hashlib, json, uuid

from repository_manager import RepositoryManager
from db.commits_db import CommitsDB
from llm.openai_llm import OpenAILLM
from function.generate_atomic_commits import generate_atomic_commits
from function.generate_suggested_commit_groups import generate_suggested_commit_groups_agglomerative

router = APIRouter()

# -----------------------------
# Pydantic models
# -----------------------------
class RepoRequest(BaseModel):
    repo_path: str

class CommitGroupRequest(RepoRequest):
    name: str

class MoveDiffRequest(RepoRequest):
    diff_id: str
    target_group_id: str

# -----------------------------
# Helpers
# -----------------------------
def get_repo_manager():
    from db.repo_db import RepoDB
    db = RepoDB()
    manager = RepositoryManager(db)
    try:
        yield manager
    finally:
        db.close()

def get_commits_db(repo_path: str):
    return CommitsDB(repo_path)

# -----------------------------
# 1️⃣ 自动加载 /commit_groups
# -----------------------------
@router.get("/commit_groups")
def get_commit_groups(
    repo_path: str = Query(...),
    manager: RepositoryManager = Depends(get_repo_manager)
):
    db = get_commits_db(repo_path)
    repo = manager.get_repository(repo_path)

    # 1. 获取 index 与 HEAD 的 diff
    diff_dicts = repo.diff_with_head()

    # 2. 计算 diff hash
    diff_hash = hashlib.sha256(json.dumps(diff_dicts, sort_keys=True).encode("utf-8")).hexdigest()
    last_hash = db.get_last_index_hash()

    if diff_hash != last_hash:
        print("[commit_groups] repo changed, regenerating atomic diffs + groups")

        # 3. 重新生成 atomic diffs
        llm = OpenAILLM(model="gpt-4o-mini")
        atomic_diffs = generate_atomic_commits(llm, diff_dicts)

        # 4. 聚合建议 groups
        suggested_groups = generate_suggested_commit_groups_agglomerative(atomic_diffs)

        print(suggested_groups)

        # 5. 更新 DB
        db.clear_all_groups()
        db.clear_all_atomic_diffs()
        for d in atomic_diffs:
            db.add_atomic_diff(
                diff_id=d["id"],
                file=d["file"],
                old_lines=d["old_lines"],
                new_lines=d["new_lines"]
            )

        for g in suggested_groups:
            db.create_commit_group(g["id"], g["name"])
            db.set_group_diffs(g["id"], [d["id"] for d in g["diffs"]])

        db.set_last_index_hash(diff_hash)

    groups = db.list_commit_groups()
    db.close()
    return {"groups": groups}

# -----------------------------
# 2️⃣ 拖拽 atomic diff
# -----------------------------
@router.post("/commit_groups/move_diff")
def move_diff(req: MoveDiffRequest):
    db = get_commits_db(req.repo_path)
    db.move_diff_to_group(req.diff_id, req.target_group_id)
    db.close()
    return {"status": "ok"}

# -----------------------------
# 3️⃣ 新建 group
# -----------------------------
@router.post("/commit_groups")
def create_commit_group(req: CommitGroupRequest):
    db = get_commits_db(req.repo_path)
    group_id = str(uuid.uuid4())
    db.create_commit_group(group_id, req.name)
    db.close()
    return {"id": group_id, "name": req.name}

# -----------------------------
# 4️⃣ 删除空 group
# -----------------------------
@router.delete("/commit_groups/{group_id}")
def delete_commit_group(group_id: str, repo_path: str = Query(...)):
    db = get_commits_db(repo_path)
    groups = db.list_commit_groups()
    group = next((g for g in groups if g["id"] == group_id), None)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group["diff_ids"]:
        raise HTTPException(status_code=400, detail="Cannot delete non-empty group")

    db.delete_commit_group(group_id)
    db.close()
    return {"status": "ok"}

# -----------------------------
# 获取 atomic diffs
# -----------------------------
@router.get("/atomic_diffs")
def get_atomic_diffs(repo_path: str = Query(...)):
    db = get_commits_db(repo_path)
    diffs = db.list_commit_groups()  # <-- 注意 atomic diffs 要单独返回
    db.close()

    # 返回 {diff_id: diff_detail}
    db = get_commits_db(repo_path)
    c = db.conn.cursor()
    c.execute("SELECT diff_id, file, old_lines, new_lines FROM atomic_diffs")
    diff_details = {}
    for row in c.fetchall():
        diff_id, file, old_lines, new_lines = row
        diff_details[diff_id] = {
            "file": file,
            "old_lines": json.loads(old_lines),
            "new_lines": json.loads(new_lines)
        }
    db.close()
    return {"diffDetails": diff_details}
