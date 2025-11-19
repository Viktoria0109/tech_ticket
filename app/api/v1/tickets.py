from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.ticket import TicketCreate, TicketRead
from app.crud import crud_ticket
from app.dependencies.roles import require_role
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.post("/", response_model=TicketRead)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud_ticket.create_ticket(db, ticket, user_id=current_user.id)

@router.get("/", response_model=list[TicketRead])
def list_tickets(q: str | None = Query(None), status: str | None = Query(None), assigned_to: int | None = Query(None), db: Session = Depends(get_db)):
    if q or status or assigned_to:
        return crud_ticket.get_filtered_tickets(db, status=status, assigned_to=assigned_to, q=q)
    return crud_ticket.list_tickets(db)

@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, confirm: bool = False, db: Session = Depends(get_db), admin: User = Depends(require_role(4))):
    ticket = crud_ticket.soft_delete_ticket(db, ticket_id, confirmed=confirm)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"ok": True, "deleted_at": ticket.deleted_at}
