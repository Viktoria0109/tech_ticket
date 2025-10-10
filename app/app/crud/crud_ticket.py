from sqlalchemy.orm import Session
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate

def create_ticket(db: Session, ticket_data: TicketCreate, user_id: int):
    ticket = Ticket(**ticket_data.dict(), created_by_id=user_id)
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

def list_tickets(db: Session):
    return db.query(Ticket).all()

