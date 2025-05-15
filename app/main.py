from contextlib import asynccontextmanager

import toml
from aiohttp import ClientSession
from fastapi import FastAPI

from app import route
from app.data import app_data
from app.error.database import UnsupportedDatabaseError
from app.logger import logger
from app.model import constants
from app.model import metadata
from app.model.data import Config, DatabaseManager
from app.util.file import new_empty_config
from app.util.auth import generate_password_hash, AuthMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        app_data.client = ClientSession(
            headers=constants.REQUEST_HEADERS
        )
        config = app_data.config = Config(**toml.load(constants.CONFIG_FILE))

        database = app_data.config.database

        if database.type not in constants.DB_PATH:
            raise UnsupportedDatabaseError(database.type)

        db = app_data.db = DatabaseManager(constants.DB_PATH[database.type])

        async with db.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

        yield
    except FileNotFoundError:
        logger.info(f"Not found config file, waiting for creation... ")
        new_empty_config(app_data)
        yield
    except Exception as e:
        logger.error(f"Failed to initialize essential resources: {str(e)}")
    finally:
        await app_data.client.close()


app = FastAPI(
    title="raven-client",
    description="LLM Client",
    lifespan=lifespan
)
route.register(app)

app.add_middleware(
    AuthMiddleware, # type: ignore
    exclude_paths=[
        "/auth/login",
        "/auth/register",
        "/docs",
        "/openapi.json",
    ],
)