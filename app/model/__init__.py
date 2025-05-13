from typing import Generic, Optional, TypeVar

from pydantic import BaseModel
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

T = TypeVar("T")
metadata = MetaData()
Base = declarative_base(metadata=metadata)

from .user import User
from .session import Session, ChatHistory

MODELS = [User, Session, ChatHistory]


class Response(BaseModel, Generic[T]):
    message: str
    data: Optional[T] = None
    success: bool

    def __init__(self, message: str, data: Optional[T] = None, success: bool = True):
        super().__init__(message=message, data=data, success=success)
