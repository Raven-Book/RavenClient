import secrets
from dataclasses import dataclass
from typing import Optional, Dict, List

from aiohttp import ClientSession
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


class ApiKey(BaseModel):
    wolfram: str = ""
    openai: str = ""


class DataBase(BaseModel):
    """ 数据库设置 """
    type: str = "sqlite"


class Provider(BaseModel):
    """ 提供商信息 """
    enabled: bool = True
    api_key: str = ""
    base_url: str = ""
    default_model: str = ""
    organization_id: Optional[str] = None


class Config(BaseModel):
    """ TOML配置 """
    secret: str = "secret-key"
    database: Optional[DataBase] = DataBase()
    providers: Dict[str, Provider] = {}
    apikey: ApiKey = ApiKey()

    def dump(self) -> Dict:
        data = self.model_dump()
        return {
            key: value for key, value in data.items()
            if value is not None and not
               ((isinstance(value, Dict) and len(value) == 0) or
                (isinstance(value, List) and len(value) == 0))
        }

    @classmethod
    def empty(cls) -> "Config":
        config = Config()
        config.secret = secrets.token_hex(16)
        config.providers["openai"] = Provider(
            enabled=False,
            api_key="sk-xxxx-xxxx",
            base_url="https://api.openai.com/v1",
            default_model="gpt-4o"
        )
        config.providers["deepseek"] = Provider(
            enabled=False,
            api_key="sk-xxxx-xxxx",
            base_url="https://api.deepseek.com",
            default_model="deepseek-chat"
        )
        return config

class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=True)
        self.async_session = async_sessionmaker(
            self.engine,
            expire_on_commit=False
        )


@dataclass
class AppData:
    db: Optional[DatabaseManager] = None
    client: Optional[ClientSession] = None
    config: Optional[Config] = None
