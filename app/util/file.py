import os
import sys

import toml

import secrets
from app.logger import logger
from app.model import constants
from app.model.data import Config, AppData


def get_app_path() -> str:
    if getattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


def new_empty_config(app_data: AppData):
    os.makedirs(constants.SAVE_DATA_DIR, exist_ok=True)
    with open(constants.CONFIG_FILE, 'w') as f:
        config = Config.empty()
        toml.dump(config.dump(), f)
        app_data.config = config
    logger.info(f'New config file created: {constants.CONFIG_FILE}')
