from fastapi import FastAPI

from app import routes

app = FastAPI()
routes.register(app)
