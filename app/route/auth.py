from asyncio import current_task
from uuid import uuid4

from sqlalchemy import or_

import bcrypt
from fastapi import APIRouter
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, async_scoped_session

from app.logger import logger
from app.model import Response, User
from app.model.data import AppData
from app.model.user import insert_users
from app.util import time

router = APIRouter()

# --- 请求响应模型 ---
class UserRegisterRequest(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserLoginRequest(BaseModel):
    username: str
    password: str

class LoginResponseData(BaseModel):
    user_id: str
    username: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        print(f"密码验证失败: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

@router.post("/login")
async def login(login_data: UserLoginRequest) -> Response[LoginResponseData] | Response[str]:
    # TODO 登录逻辑
    try:
        # 查询用户
        session = async_scoped_session(AppData.db.async_session, scopefunc=current_task)
        result = await session.execute(
            select(User).where(or_(User.username == login_data.username))
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(login_data.password, user.password_hash):
            logger.error("无效的账号或错误的密码")
            return Response[LoginResponseData](
            success=False,
            message="登录失败",
            data=LoginResponseData(
                user_id=user.id,
                username=user.username
            )
        )
        user.last_login = time.utcnow()
        await session.commit()
        return Response[LoginResponseData](
            success=True,
            message="登录成功",
            data=LoginResponseData(
                user_id=user.id,
                username=user.username
            )
        )
    except Exception as e:
        print(f"登录失败: {str(e)}")
        return Response(
            success=False,
            message="登录失败",
            data=str(e)
        )

@router.post("/register")
async def register(user_data: UserRegisterRequest) -> Response[UserRegisterRequest] | Response[str]:
    # TODO 注册逻辑
    try:
        # 检查用户是否存在
        session = async_scoped_session(AppData.db.async_session, scopefunc=current_task)
        existing_user = await session.execute(
            select(User).where(
                or_(
                    User.username == user_data.username,
                    User.email == user_data.email
                )
            )
        )

        if existing_user.scalar_one_or_none():
            return Response(
                message="注册失败",
                data=user_data,
                success=False
            )

        # 创建用户对象
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            api_key=str(uuid4())  # 生成随机API密钥
        )

        await insert_users(AppData.db.async_session, new_user)

    except Exception as e:
        logger.error("注册用户发生异常：",str(e))
    return Response(
        message="注册成功",
        data=user_data,
        success=True
    )