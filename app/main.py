
from fastapi import FastAPI
from app.api.v1 import tickets
from app.api.v1 import auth
from app.database import Base, engine
from app.models import user, ticket
from app.models.comment import Comment
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.include_router(tickets.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="frontent/static"), name="static")
templates = Jinja2Templates(directory="templates")

