from typing import Dict
from uuid import uuid4

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, JSON
)

from app.model import Base
from app.util import time


class Session(Base):
    __tablename__ = "session"

    id = Column('id', String(36), primary_key=True, default=lambda: str(uuid4()), comment="会话ID")
    user_id = Column('user_id', Integer, comment="用户ID")
    title = Column('title', String(255), default="新对话", comment="会话标题")
    created_at = Column('created_at', DateTime, default=time.utcnow, comment="创建时间")
    updated_at = Column('updated_at', DateTime, default=time.utcnow, onupdate=time.utcnow, comment="更新时间")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column('id', String(36), primary_key=True, default=lambda: str(uuid4()), comment="消息ID")
    session_id = Column('session_id', String(36), comment="会话ID")
    message_type = Column('message_type', String(10), comment="消息类型")
    content = Column('content', Text, comment="消息内容")
    model_used = Column('model_used', String(50), comment="模型")
    order = Column('order', Integer, comment="消息顺序")
    prompt_tokens = Column('prompt_tokens', Integer, default=0, comment="prompt tokens")
    completion_tokens = Column('completion_tokens', Integer, default=0, comment="completion tokens")
    request_params = Column('request_params', JSON, comment="请求参数")
    create_at = Column('create_at', DateTime, default=time.utcnow, comment="创建时间")