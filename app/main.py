from fastapi import FastAPI
from app.api.v1 import tickets
from app.database import Base, engine
from app.models import user, ticket, comment 
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.include_router(tickets.router, prefix="/api/v1")

Base.metadata.create_all(bind=engine)


app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
