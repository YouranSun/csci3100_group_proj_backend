# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import multiprocessing
import uvicorn
import sys
import time
import time

# routers
from router.repo_router import router as repo_router
from router.summary_router import router as summary_router
from router.commits_router import router as commits_router
from router.commit_message_router import router as commit_message_router
from router.insights_router import router as insights_router
from router.user_router import router as user_router
from router.label_commits_router import router as label_commits_router

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 打包阶段先放开
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repo_router)
app.include_router(summary_router)
app.include_router(commits_router)
app.include_router(commit_message_router)
app.include_router(insights_router)
app.include_router(user_router)
app.include_router(label_commits_router)

def main():
    print("=== BACKEND START ===", flush=True)

    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        reload=False,     # ❗必须
        workers=1,        # ❗必须
        loop="asyncio"    # ❗明确
    )

    server = uvicorn.Server(config)
    server.run()          # ← 不要用 uvicorn.run()

if __name__ == "__main__":
    print("=== PROCESS START ===", flush=True)
    multiprocessing.freeze_support()
    main()
