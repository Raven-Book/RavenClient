from uuid import uuid4

from sqlalchemy import (
    Table, Column, Integer, String, Text, Boolean,
    DateTime, JSON
)

from app.model import metadata
from app.utils import time

Session = Table(
    'session',
    metadata,
    Column('id', String(36), primary_key=True, default=lambda: str(uuid4()), comment="会话ID"),
    Column('user_id', Integer, nullable=False, comment="用户ID"),
    Column('title', String(255), default="新对话", comment="会话标题"),
    Column('created_at', DateTime, default=time.utcnow, comment="创建时间"),
    Column('updated_at', DateTime, default=time.utcnow, onupdate=time.utcnow, comment="更新时间")
)

ChatHistory = Table(
    'chat_history',
    metadata,
    Column('id', Integer, primary_key=True, comment="消息ID"),
    Column('session_id', String(36), nullable=False, comment="会话ID"),
    Column('message_type', String(10), nullable=False, comment="消息类型"),
    Column('content', Text, nullable=False, comment="消息内容"),
    Column('model_used', String(50), comment="模型"),
    Column('order', Integer, nullable=False, comment="消息顺序"),
    Column('prompt_tokens', Integer, default=0, comment="prompt tokens"),
    Column('completion_tokens', Integer, default=0, comment="completion tokens"),
    Column('request_params', JSON, comment="请求参数"),
    Column('create_at', DateTime, default=time.utcnow, comment="创建时间"),

)