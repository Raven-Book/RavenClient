from fastapi import FastAPI

app = FastAPI()


@app.get("/say")
def read_root():
    return {"Hello": "World"}