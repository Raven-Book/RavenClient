import asyncio

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from app.model import Response

router = APIRouter()


@router.get("/stream_test")
async def stream_test():
    async def generator():
        text = "咕咕嘎嘎。咕咕嘎嘎！"
        for _ in range(5):
            for char in text:
                await asyncio.sleep(0.1)
                yield char.encode()
    return StreamingResponse(
        content=generator(),
        media_type="text/plain"
    )

