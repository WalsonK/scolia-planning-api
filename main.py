from typing import Union

from fastapi import FastAPI

from libs.rustml_wrapper import Rustml 

app = FastAPI()
rustml = Rustml()

@app.get("/")
def read_root():
    return {"Hello": "World"}