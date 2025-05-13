from sqlalchemy import (
    Table, Column,
    Integer, String, Boolean,
    DateTime
)

from app.model import metadata
from app.util import time

User = Table(
    'user',
    metadata,
    Column('id', Integer, primary_key=True, comment="用户ID"),
    Column('username', String(50), unique=True, nullable=False, comment="用户名"),
    Column('email', String(100), nullable=False, comment="邮箱"),
    Column('password_hash', String(128), nullable=False, comment="密码"),
    Column('is_active', Boolean, default=True, comment="是否激活"),
    Column('api_key', String(64), unique=True, comment="API密钥"),
    Column('last_login', DateTime, comment="最后登录时间"),
    Column('created_at', DateTime, default=time.utcnow, comment="创建时间"),
    Column('updated_at', DateTime, default=time.utcnow, onupdate=time.utcnow, comment="更新时间"),
)
