# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router.repo_router import router as repo_router
from router.summary_router import router as summary_router
from router.commits_router import router as commits_router
from router.commit_message_router import router as commit_message_router
from router.insights_router import router as insights_router
from router.user_router import router as user_router

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(repo_router)
app.include_router(summary_router)
app.include_router(commits_router)
app.include_router(commit_message_router)
app.include_router(insights_router)
app.include_router(user_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host="127.0.0.1", port=8001, reload=True, log_level="debug"
    )
