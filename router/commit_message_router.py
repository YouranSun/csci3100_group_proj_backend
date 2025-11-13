# router/commit_message_router.py
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List
from llm.openai_llm import OpenAILLM
from function.generate_commit_message import generate_commit_message, summarize_diff
from db.commits_db import CommitsDB

router = APIRouter()

# -----------------------------
# Models
# -----------------------------
class CommitMessageRequest(BaseModel):
    repo_path: str
    group_id: str

class EditCommitMessageRequest(CommitMessageRequest):
    message: str

# -----------------------------
# Helpers
# -----------------------------
def get_commits_db(repo_path: str):
    return CommitsDB(repo_path)

# -----------------------------
# 1️⃣ 生成 commit message
# -----------------------------
@router.post("/commit_message/generate")
def generate_group_commit_message(req: CommitMessageRequest):
    db = get_commits_db(req.repo_path)

    # 获取 group diff_ids
    c = db.conn.cursor()
    c.execute("SELECT diff_id FROM commit_group_diffs WHERE group_id=?", (req.group_id,))
    diff_ids = [r[0] for r in c.fetchall()]
    if not diff_ids:
        db.close()
        raise HTTPException(status_code=404, detail="Group not found or empty")

    # 拉取 diff 详细内容
    diff_dicts = []
    for diff_id in diff_ids:
        diff = db.get_diff(diff_id)
        if diff:
            diff_dicts.append(diff)

    llm = OpenAILLM(model="gpt-4o-mini")
    message = generate_commit_message(llm, diff_dicts)

    # 保存到 metadata 表里，以 group_id 为 key
    c.execute(
        "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
        (f"commit_message:{req.group_id}", message)
    )
    db.conn.commit()
    db.close()
    return {"group_id": req.group_id, "message": message}

# -----------------------------
# 2️⃣ 获取 commit message
# -----------------------------
@router.get("/commit_message")
def get_commit_message(repo_path: str = Query(...), group_id: str = Query(...)):
    db = get_commits_db(repo_path)
    c = db.conn.cursor()
    c.execute("SELECT value FROM metadata WHERE key=?", (f"commit_message:{group_id}",))
    row = c.fetchone()
    db.close()
    if row:
        return {"group_id": group_id, "message": row[0]}
    return {"group_id": group_id, "message": ""}

# -----------------------------
# 3️⃣ 编辑 commit message
# -----------------------------
@router.post("/commit_message/edit")
def edit_commit_message(req: EditCommitMessageRequest):
    db = get_commits_db(req.repo_path)
    c = db.conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
        (f"commit_message:{req.group_id}", req.message)
    )
    db.conn.commit()
    db.close()
    return {"group_id": req.group_id, "message": req.message}
