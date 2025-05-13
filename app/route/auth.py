from fastapi import APIRouter

from app.model import Response

router = APIRouter()

@router.post("/login")
async def login():
    # TODO 登录逻辑
    pass

@router.post("/register")
async def register() -> Response[str]:
    # TODO 注册逻辑
    return Response(
        message="注册成功",
        data="数据格式",
        success=True
    )