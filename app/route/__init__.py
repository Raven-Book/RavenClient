from fastapi import FastAPI

from .auth import router as auth
from .llm import router as llm

__all__ = ["auth", "llm"]


def register(app: FastAPI):
    app.include_router(auth, prefix="/auth")
    app.include_router(llm, prefix="/llm")