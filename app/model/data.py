from dataclasses import dataclass
from typing import Optional

from aiohttp import ClientSession
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


class ApiKey(BaseModel):
    wolfram: str = ""
    openai: str = ""


class DataBase(BaseModel):
    type: str = "sqlite"


class Config(BaseModel):
    apikey: Optional[ApiKey] = ApiKey()
    database: Optional[DataBase] = DataBase()


class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url)
        self.async_session = async_sessionmaker(
            self.engine,
            expire_on_commit=False
        )


@dataclass
class AppData:
    db: Optional[DatabaseManager] = None
    client: Optional[ClientSession] = None
    config: Optional[Config] = None
