from typing import Dict

from app.main import app_data

url = "https://api.wolframalpha.com/v2/query"

async def query(params: Dict[str, str]):
    res = await app_data.client.get(url, params=params)
