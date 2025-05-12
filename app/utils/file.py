import os
import sys

import toml

from app.logger import logger
from app.models import constants
from app.models.data import Config, AppData


def get_app_path() -> str:
    if getattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


def new_empty_config(app_data: AppData):
    os.makedirs(constants.SAVE_DATA_DIR, exist_ok=True)
    with open(constants.CONFIG_FILE, 'w') as f:
        config = Config()
        toml.dump(config.model_dump(), f)
        app_data.config = config
    logger.info(f'New config file created: {constants.CONFIG_FILE}')
