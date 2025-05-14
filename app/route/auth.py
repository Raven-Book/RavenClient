from uuid import uuid4

from fastapi import APIRouter
from sqlalchemy import or_
from sqlalchemy import select

from app.data import app_data
from app.logger import logger
from app.model import Response, User
from app.model.user import insert_users, UserLoginRequest, LoginResponseData, UserRegisterRequest
from app.util import time
from app.util.auth import generate_password_hash, verify_password

router = APIRouter()


@router.post("/login")
async def login(login_data: UserLoginRequest) -> Response[LoginResponseData] | Response[str]:
    try:
        async with app_data.db.async_session() as session:
            result = await session.execute(
                select(User).where(or_(User.username == login_data.username))
            )
            user = result.scalar_one_or_none()

            if not user or not verify_password(login_data.password, user.password_hash):
                return Response[LoginResponseData](
                    success=False,
                    message="无效的账号或错误的密码",
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
        logger.error(f"登录失败: {str(e)}")
        return Response(
            success=False,
            message="登录失败",
            data=str(e)
        )


@router.post("/register")
async def register(user_data: UserRegisterRequest) -> Response[UserRegisterRequest] | Response[str]:
    try:
        async with app_data.db.async_session() as session:
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
                    message="用户名或邮箱已存在",
                    data=user_data,
                    success=False
                )

            new_user = User(
                username=user_data.username,
                email=str(user_data.email),
                password_hash=generate_password_hash(user_data.password),
                api_key=str(uuid4())
            )

            await insert_users(app_data.db.async_session, [new_user])

    except Exception as e:
        logger.error("注册用户发生异常：", str(e))
    return Response(
        message="注册成功",
        data=user_data,
        success=True
    )
