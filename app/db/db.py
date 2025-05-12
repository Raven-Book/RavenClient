from datetime import datetime
from typing import Type, Optional
from uuid import uuid4

import bcrypt
from sqlalchemy import create_engine, Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.types import (
    Integer, String, Text, Boolean,
    DateTime, JSON
)

from app.logger import logger

Base = declarative_base()


def _generate_password_hash(password: str) -> Optional[bytes]:
    """安全生成密码哈希（包含自动生成的盐）"""
    try:
        if not password:
            raise ValueError("密码不能为空")

        # 将密码字符串转换为bytes
        password_bytes = password.encode('utf-8')

        # 生成带盐的哈希值
        return bcrypt.hashpw(password_bytes, bcrypt.gensalt(12))
    except Exception as e:
        # 实际应用中应记录日志
        logger.error(f"生成密码哈希失败: {str(e)}")
        return None


def _check_password_hash(password: str, hashed: bytes) -> bool:
    """安全验证密码与哈希是否匹配"""
    try:
        if not password or not hashed:
            return False

        password_bytes = password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed)
    except (ValueError, TypeError) as e:
        # 处理无效哈希或类型错误
        logger.info(f"密码验证异常: {str(e)}")
        return False

# ---------- 数据模型 ----------
class User(Base):
    """ 用户表模型 """
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    api_key = Column(String(64), unique=True)

    # 关系定义
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str) -> bool:
        """安全设置密码"""
        hashed = _generate_password_hash(password)
        if not hashed:
            return False

        try:
            # 将bytes转换为字符串存储
            self.password_hash = hashed.decode('utf-8')
            return True
        except UnicodeDecodeError:
            print("哈希值解码失败")
            return False

    def check_password(self, password: str) -> bool:
        """验证密码是否正确"""
        if not self.password_hash:
            return False

        try:
            # 将存储的字符串转换回bytes
            hashed_bytes = self.password_hash.encode('utf-8')
            return _check_password_hash(password, hashed_bytes)
        except UnicodeEncodeError:
            print("哈希值编码失败")
            return False

    @classmethod
    def create_user(cls, username: str, email: str, password: str) -> 'User':
        """ 快速创建用户方法 """
        user = cls(username=username, email=email)
        user.set_password(password)
        return user


class Session(Base):
    """ 会话表模型 """
    __tablename__ = 'sessions'
    __table_args__ = (
        UniqueConstraint('user_id', 'order', name='uq_user_order'),
    )

    session_id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete="CASCADE"), nullable=False)
    title = Column(String(255), default="新对话")
    order = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系定义
    user = relationship("User", back_populates="sessions")
    chat_records = relationship("ChatRecord", back_populates="session", cascade="all, delete-orphan")

    @classmethod
    def create_session(cls, user: User, title: str = None) -> 'Session':
        """ 创建新会话并自动排序 """
        new_order = len(user.sessions) + 1
        return cls(user=user, order=new_order, title=title or f"对话{new_order}")


class ChatRecord(Base):
    """ 聊天记录表模型 """
    __tablename__ = 'chat_history'

    chat_id = Column(Integer, primary_key=True)
    session_id = Column(String(36), ForeignKey('sessions.session_id', ondelete="CASCADE"), nullable=False)
    message_type = Column(String(10), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    model_used = Column(String(50))
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_pinned = Column(Boolean, default=False)
    request_params = Column(JSON)

    # 关系定义
    session = relationship("Session", back_populates="chat_records")

    @classmethod
    def create_record(
            cls,
            session: Session,
            message_type: str,
            content: str,
            model: str = None,
            prompt_tokens: int = 0,
            completion_tokens: int = 0
    ) -> 'ChatRecord':
        """ 快速创建记录方法 """
        return cls(
            session=session,
            message_type=message_type,
            content=content,
            model_used=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens
        )


# ---------- 数据库管理类 ----------
class DatabaseManager:
    def __init__(self, database_url: str = "sqlite:///chat.db"):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)

    def initialize_database(self):
        """ 初始化数据库表结构 """
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """ 获取新的会话对象 """
        return self.Session()

    # ---------- 常用操作方法 ----------
    def add_user(self, username: str, email: str, password: str) -> User:
        """ 添加新用户 """
        with self.get_session() as session:
            user = User.create_user(username, email, password)
            session.add(user)
            session.commit()
            return user

    def get_user_sessions(self, user_id: int) -> list[Type[Session]]:
        """ 获取用户的所有会话（按order排序） """
        with self.get_session() as db_session:
            query = db_session.query(Session).filter_by(user_id=user_id)
            ordered_query = query.order_by(Session.order.asc())
            return ordered_query.all()  # 类型推断器现在能正确识别返回类型

    def add_chat_record(
            self,
            session_id: str,
            message_type: str,
            content: str,
            **kwargs
    ) -> ChatRecord:
        """ 添加聊天记录 """
        with self.get_session() as session:
            chat_record = ChatRecord.create_record(
                session=session.query(Session).get(session_id),
                message_type=message_type,
                content=content,
                **kwargs
            )
            session.add(chat_record)
            session.commit()
            return chat_record

    def update_session_order(self, session_id: str, new_order: int):
        """ 更新会话排序 """
        with self.get_session() as session:
            target = session.query(Session).get(session_id)
            original_order = target.order

            # 调整其他会话的order值
            if new_order > original_order:
                session.query(Session).filter(
                    Session.user_id == target.user_id,
                    Session.order > original_order,
                    Session.order <= new_order
                ).update({"order": Session.order - 1})
            else:
                session.query(Session).filter(
                    Session.user_id == target.user_id,
                    Session.order >= new_order,
                    Session.order < original_order
                ).update({"order": Session.order + 1})

            target.order = new_order
            session.commit()