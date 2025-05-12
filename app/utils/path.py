import os
import sys


def get_app_path() -> str:
    if getattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)
