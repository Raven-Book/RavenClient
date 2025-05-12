from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.logger import logger

from app import routes
from app.client import client


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        yield
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
    finally:
        await client.close()


app = FastAPI(
    title="raven-client",
    description="LLM Client",
    lifespan=lifespan
)
routes.register(app)
