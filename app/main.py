
from fastapi import FastAPI, Depends
from . import models 
from app.api.v1 import tickets
from app.api.v1 import auth
from app.db.session import Base, engine, get_db
from app.models import user, ticket
from app.models.comment import Comment
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI()


Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root(db = Depends(get_db)):
    return {"ok": True}


app.include_router(tickets.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")


Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="frontent/static"), name="static")
templates = Jinja2Templates(directory="frontent/templates")

BASE_DIR = Path(__file__).resolve().parent.parent

from app.api.v1.users import create_admin_if_not_exists