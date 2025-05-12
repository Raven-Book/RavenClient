from typing import Dict

from app.client import client

url = "https://api.wolframalpha.com/v2/query"

async def query(params: Dict[str, str]):
    res = await client.get(url, params=params)
