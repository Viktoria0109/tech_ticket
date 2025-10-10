from fastapi import FastAPI
from app.api.v1 import tickets

app = FastAPI()

app.include_router(tickets.router, prefix="/api/v1")

