from typing import Optional, List
from uuid import uuid4

from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    Column,
    String, Boolean,
    DateTime, select
)
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.model import Base
from app.util import time


class User(Base):
    __tablename__ = 'user'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()), comment="用户ID")
    username = Column(String(50), unique=True, comment="用户名")
    email = Column(String(100), comment="邮箱")
    password_hash = Column(String(128), comment="密码")
    is_active = Column(Boolean, default=True, comment="是否激活")
    api_key = Column(String(64), nullable=True, unique=True, comment="API密钥")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")
    created_at = Column(DateTime, default=time.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=time.utcnow, onupdate=time.utcnow, comment="更新时间")


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
    api_key: Optional[str]


async def get_user_by_id(session: async_sessionmaker, user_id: int) -> Optional[User]:
    async with session() as session:
        query = select(User).where(User.id == user_id)  # type: ignore
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def insert_users(session: async_sessionmaker, users: List[User]) -> None:
    async with session() as session:
        async with session.begin():
            session.add_all(users)
