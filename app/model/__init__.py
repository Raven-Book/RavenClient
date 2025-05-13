from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)

from .user import User
from .session import Session, ChatHistory

MODELS = [User, Session, ChatHistory]
