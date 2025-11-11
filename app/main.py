
import os
from pathlib import Path
from fastapi import FastAPI,Depends,Request,HTTPException,status,Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.db.base import init_db
from app.db.session import get_db, SessionLocal
from app.api.v1 import tickets as ticket_router, auth as auth_router, users as users_router
from app.api.v1.users import create_admin_if_not_exists
from app import models, schemas
from app.dependencies.roles import require_role
from app.models import User 
from app.core.security import get_current_user, verify_password, create_access_token, get_password_hash
from app.core.config import settings
from app.crud.crud_user import get_user_by_email, create_user, list_users


app = FastAPI()

@app.on_event("startup")
def on_startup() -> None:
    init_db()
    with SessionLocal() as db:
        create_admin_if_not_exists(db)

app.include_router(users_router.router, prefix="/api/v1")
app.include_router(ticket_router.router, prefix="/api/v1")
app.include_router(auth_router.router, prefix="/api/v1")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontent") 

app.mount( "/static",StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")),name="static",)
templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))

templates.env.globals["static_url"] = "/static"
templates.env.globals["app_name"] = "Система заявок"

@app.get("/favicon.ico")
def favicon():
    favicon_path = FRONTEND_DIR / "static" / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(str(favicon_path))
    raise HTTPException(status_code=404)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

ROLE_REDIRECT = {
    4: "/admin",       
    2: "/menager",     
    3: "/technic",     
    1: "/user",        
}

@app.post("/login")
def login_form(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email)
    if not db_user or not verify_password(password, db_user.hashed_password):
        return templates.TemplateResponse("auth/login.html", {"request": request, "error": "Неверный email или пароль"}, status_code=401)

    # создаём токен и кладём туда id и роль
    token = create_access_token(data={"sub": str(db_user.id), "role": int(db_user.role)})

    redirect_url = ROLE_REDIRECT.get(int(db_user.role), "/")
    resp = RedirectResponse(url=redirect_url, status_code=303)
    resp.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=60*60*24,
        samesite="lax",
        secure=False,
        path="/"
    )
    return resp

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
            hashed_password=get_password_hash(password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/login", status_code=303) 




@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, current_user: User = Depends(get_current_user)):
    #if current_user.role != 4:
        #raise HTTPException(status_code=403)
    return templates.TemplateResponse("admin/admin.html", {"request": request, "user": current_user})


@app.get("/user", response_class=HTMLResponse)
def user_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("user/user.html", {"request": request, "user": current_user})
