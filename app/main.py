
import os
from pathlib import Path
from fastapi import FastAPI, Depends, Request, HTTPException, Form
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

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontent"
ALLOWED_PRIORITIES = ["низкий", "средний", "высокий"]

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(FRONTEND_DIR / "templates"))

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

@app.get("/logout")
def logout():
    resp = RedirectResponse(url="/login", status_code=303)
    resp.delete_cookie("access_token")
    return resp

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": current_user})

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 401:
        return RedirectResponse(url="/login")
    raise exc

@app.get("/admin/users/add", response_class=HTMLResponse)
def admin_add_user_page(request: Request, current_user: User = Depends(require_role(4))):
    return templates.TemplateResponse("admin/add_user.html", {"request": request, "user": current_user})

@app.post("/admin/users/create")
def admin_create_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: int = Form(1),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(4))
):
    user_in = schemas.UserCreate(name=name, email=email, password=password, role=role)
    create_user(db, user_in)
    return RedirectResponse(url="/admin/users", status_code=303)

@app.get("/admin/users", response_class=HTMLResponse)
def admin_users_list(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_role(4))):
    users = list_users(db)
    return templates.TemplateResponse("admin/users.html", {"request": request, "users": users, "user": current_user})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@app.post("/register")
async def register_user(request: Request, name: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if get_user_by_email(db, email):
        return templates.TemplateResponse("auth/register.html", {"request": request, "error": "Email уже зарегистрирован"}, status_code=400)
    new_user = User(name=name, email=email, hashed_password=get_password_hash(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return RedirectResponse(url="/login", status_code=303)

@app.get("/session-info")
def session_info(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Вы авторизованы как {current_user.name}",
        "session_valid_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    }

# Страница назначения заявки
@app.get("/tickets/{ticket_id}/assign", response_class=HTMLResponse)
def assign_ticket_page(
    request: Request,
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([2, 4]))  # менеджер или админ
):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # список доступных техников (роль = 3)
    technicians = db.query(models.User).filter(models.User.role == 3).all()

    return templates.TemplateResponse(
        "tickets/assign.html",
        {
            "request": request,
            "ticket": ticket,
            "technicians": technicians,
            "user": current_user
        }
    )

# Обработчик назначения заявки
@app.post("/tickets/{ticket_id}/assign")
def assign_ticket(
    ticket_id: int,
    technician_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([2, 4]))  # менеджер или админ
):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.assigned_to = technician_id
    db.commit()
    return RedirectResponse(url="/tickets/list", status_code=303)

@app.post("/create-ticket", response_class=HTMLResponse)
def create_ticket_form(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    priority: str = Form("средний"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # нормализуем ввод
    priority = priority.lower()

    if priority not in ALLOWED_PRIORITIES:
        raise HTTPException(status_code=400, detail="Недопустимый приоритет")

    db_ticket = models.Ticket(
        title=title,
        description=description,
        priority=priority,
        user_id=current_user.id
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return RedirectResponse(url="/tickets/list", status_code=303)

@app.post("/tickets", response_model=schemas.ticket.TicketRead)
def create_ticket_web(ticket: schemas.ticket.TicketCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_ticket = models.Ticket(**ticket.dict())
    db_ticket.user_id = current_user.id
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@app.get("/tickets", response_model=list[schemas.ticket.TicketRead])
def read_tickets(db: Session = Depends(get_db)):
    return db.query(models.Ticket).filter(models.Ticket.is_deleted == False).all()

@app.get("/tickets/list", response_class=HTMLResponse)
def tickets_list_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Получаем все заявки из базы, которые не удалены
    tickets = db.query(models.Ticket).filter(models.Ticket.is_deleted == False).all()

    # 2. Определяем возможные статусы и приоритеты для фильтра
    statuses = ["новая", "в работе", "закрыта"]
    priorities = ["низкий", "средний", "высокий"]

    # 3. Передаём данные в шаблон ticket/list.html
    return templates.TemplateResponse(
        "tickets/list.html",
        {
            "request": request,
            "tickets": tickets,          # список заявок
            "statuses": statuses,        # список статусов
            "priorities": priorities,    # список приоритетов
            "current_user": current_user # текущий пользователь
        }
    )

@app.get("/tickets/{ticket_id}", response_model=schemas.ticket.TicketRead)
def read_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id, models.Ticket.is_deleted == False).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ticket.is_deleted = True
    ticket.deleted_at = None
    db.commit()
    return {"message": "Ticket deleted"}

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("admin/admin.html", {"request": request, "user": current_user})

@app.get("/user", response_class=HTMLResponse)
def user_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("user/user.html", {"request": request, "user": current_user})

@app.get("/menager", response_class=HTMLResponse)
def manager_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_role([2, 4]))):
   
    tickets = db.query(models.Ticket).filter(models.Ticket.is_deleted == False).all()
    return templates.TemplateResponse("menager/menager.html", {"request": request, "tickets": tickets, "user": current_user})

@app.get("/technic", response_class=HTMLResponse)
def technic_page(request: Request, db: Session = Depends(get_db), current_user: User = Depends(require_role([3, 4]))):
   
    tickets = db.query(models.Ticket).filter(models.Ticket.is_deleted == False, models.Ticket.assigned_to == current_user.id).all()
    return templates.TemplateResponse("technic/technic.html", {"request": request, "tickets": tickets, "user": current_user})

