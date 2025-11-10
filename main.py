# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router.repo_router import router as repo_router
from router.abstract_router import router as abstract_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或者只允许你的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(repo_router)
app.include_router(abstract_router)