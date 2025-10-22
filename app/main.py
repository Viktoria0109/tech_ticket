from fastapi import FastAPI
from app.api.v1 import tickets
from app.database import Base, engine
from app.models import user, ticket, comment 


app = FastAPI()

app.include_router(tickets.router, prefix="/api/v1")

Base.metadata.create_all(bind=engine)

