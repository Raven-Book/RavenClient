from sqlalchemy import MetaData

metadata = MetaData()

from .user import User
from .session import Session, ChatHistory

MODELS = [User, Session, ChatHistory]
