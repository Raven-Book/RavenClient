from fastapi import FastAPI
from .auth import router as auth


__all__ = ["auth"]


def register(app: FastAPI):
    app.include_router(auth, prefix="/auth")


