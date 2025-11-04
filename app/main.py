
import os
from pathlib import Path
from fastapi import (FastAPI,Depends,Request,HTTPException,status,Form
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.schemas import Token, LoginRequest, UserCreate
from app.db.base import Base, engine
from app.db.session import get_db, SessionLocal
from app.api.v1 import tickets, auth, users
from app.api.v1.users import create_admin_if_not_exists
from app import models, schemas
from app.models import User, Ticket, Comment  
from app.core.security import (get_current_user,verify_password,create_access_token, get_password_hash )
from app.core.config import settings
from app.crud.crud_user import get_user_by_email, create_user
from app.models.user import hashed_password

app = FastAPI()

@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        create_admin_if_not_exists(db)

app.include_router(users.router, prefix="/api/v1")
app.include_router(tickets.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontent") 

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")),
    name="static",
)
templates = Jinja2Templates(
    directory=os.path.join(FRONTEND_DIR, "templates")
)

templates.env.globals["static_url"] = "/static"
templates.env.globals["app_name"] = "Система заявок"

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html", {"request": request}
    )

@app.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == payload.email).first()
    if not db_user or not verify_password(
        payload.password, db_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token}

@app.get("/", response_class=HTMLResponse)
def read_root(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "index.html", {"request": request, "user": current_user}
    )

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(
    request: Request, exc: StarletteHTTPException
):
    if exc.status_code == 401:
        return RedirectResponse(url="/login")
    raise exc

@app.get("/session-info")
def session_info(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Вы авторизованы как {current_user.username}",
        "session_valid_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    }

@app.post("/tickets", response_model=schemas.TicketBase)
def create_ticket(
    ticket: schemas.TicketCreate, db: Session = Depends(get_db)
):
    db_ticket = models.Ticket(**ticket.dict())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@app.get("/tickets", response_model=list[schemas.TicketBase])
def read_tickets(db: Session = Depends(get_db)):
    return db.query(models.Ticket).all()

@app.get("/tickets/{ticket_id}", response_model=schemas.TicketBase)
def read_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = (
        db.query(models.Ticket)
        .filter(models.Ticket.id == ticket_id)
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = (
        db.query(models.Ticket)
        .filter(models.Ticket.id == ticket_id)
        .first()
    )
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(ticket)
    db.commit()
    return {"message": "Ticket deleted"}


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        "auth/register.html", {"request": request}
    )

@app.post("/register")
async def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    department: str = Form(...),
    db: Session = Depends(get_db)
):
    if get_user_by_email(db, email):
            return templates.TemplateResponse(
                "auth/register.html",
                {"request": request, "error": "Email уже зарегистрирован"},
                status_code=400
            )

    new_user = User(
            username=username,
            email=email,
            department=department,
            hashed_password=hashed_password(password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/login", status_code=303)  

