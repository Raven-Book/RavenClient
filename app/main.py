from contextlib import asynccontextmanager

import toml
from aiohttp import ClientSession
from fastapi import FastAPI

from app import routes
from app.logger import logger
from app.models import constants
from app.models.data import Config, AppData
from app.utils.file import new_empty_config

app_data: AppData = AppData()


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        app_data.client = ClientSession(
            headers=constants.REQUEST_HEADERS
        )
        app_data.config = Config(**toml.load(constants.CONFIG_FILE))
        yield
    except FileNotFoundError:
        logger.info(f"Not found config file, waiting for creation... ")
        new_empty_config(app_data)
        yield
    except Exception as e:
        logger.error(f"Failed to initialize essential resources: {e}")
    finally:
        await app_data.client.close()


app = FastAPI(
    title="raven-client",
    description="LLM Client",
    lifespan=lifespan
)
routes.register(app)
