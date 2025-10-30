from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.ticket import TicketCreate, TicketRead
from app.crud import crud_ticket
from app.dependencies.roles import require_role
from app.crud.crud_user import get_user_by_email
from app.crud.crud_ticket import list_tickets, soft_delete_ticket
from app.db.session import get_db

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/tickets", response_model=TicketRead)
def create_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    return crud_ticket.create_ticket(db, ticket, user_id=1) 
@router.get("/tickets", response_model=list[TicketRead])
def list_tickets(db: Session = Depends(get_db)):
    return crud_ticket.list_tickets(db)

@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, confirm: bool = False, db: Session = Depends(get_db), admin=Depends(require_role(4))):
    ticket = crud_ticket.soft_delete_ticket(db, ticket_id, confirmed=confirm)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"ok": True, "deleted_at": ticket.deleted_at}

