from dataclasses import dataclass
from typing import Optional
from aiohttp import ClientSession

from pydantic import BaseModel


class ApiKey(BaseModel):
    wolfram: str = ""
    openai: str = ""


class Config(BaseModel):
    apikey: Optional[ApiKey] = ApiKey()

@dataclass
class AppData:
    client: Optional[ClientSession] = None
    config: Optional[Config] = None