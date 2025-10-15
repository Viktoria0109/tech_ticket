from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.ticket import TicketCreate, TicketRead
from app.crud import crud_ticket

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

