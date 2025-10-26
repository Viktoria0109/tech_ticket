from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models.ticket import Ticket
from app.models.user import User
from app.core.auth import get_current_user
from app.core.security import require_admin
from app.templates import templates

router = APIRouter()

@router.get("/admin/tickets", response_class=HTMLResponse)
def admin_ticket_list(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_admin(current_user)
    tickets = db.query(Ticket).options(
        joinedload(Ticket.creator),
        joinedload(Ticket.assignee)
    ).order_by(Ticket.created_at.desc()).all()
    return templates.TemplateResponse("admin/tickets.html", {"request": request, "tickets": tickets})

@router.post("/admin/users/add")
def add_user_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    department: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_admin(current_user)
    create_user_admin(db, username=username, email=email, password=password, role=role, department=department)
    return RedirectResponse(url="/admin", status_code=303)