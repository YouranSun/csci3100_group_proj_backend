# user_router.py
from fastapi import APIRouter, Request, Response, HTTPException
from router.router_request import UserLoginRequest, UserResponse, UserRegisterRequest
from db.user_db import UserDB

router = APIRouter(prefix="/user", tags=["user"])

db = UserDB()  # 单例数据库对象


# -----------------------------
# Routes
# -----------------------------

@router.post("/register", response_model=UserResponse)
def register(req: UserRegisterRequest):
    success = db.add_user(req.username, req.password)
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = db.get_user(req.username)
    return {"id": user[0], "username": user[1]}


@router.post("/login")
def login(req: UserLoginRequest, response: Response):
    if not db.verify_user(req.username, req.password):
        print("fail")
        raise HTTPException(status_code=401, detail="Invalid username or password")
    # 简单 session 实现，存 username
    response.set_cookie(key="user", value=req.username, httponly=True)
    print("success")
    return {"message": "Login successful", "username": req.username}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("user")
    return {"message": "Logged out"}


@router.get("/me")
def get_current_user(request: Request):
    username = request.cookies.get("user")
    if not username:
        raise HTTPException(status_code=401, detail="Not logged in")
    user = db.get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {"id": user[0], "username": user[1]}
