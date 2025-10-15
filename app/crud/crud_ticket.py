from sqlalchemy.orm import Session
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate
from app.schemas.ticket import TicketCreate, TicketUpdate


def create_ticket(db: Session, ticket: TicketCreate):
    db_ticket = Ticket(**ticket.dict())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket
def get_ticket(db: Session, ticket_id: int):
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def update_ticket(db: Session, ticket_id: int, ticket_data: TicketUpdate):
    ticket = get_ticket(db, ticket_id)
    if ticket:
        for key, value in ticket_data.dict(exclude_unset=True).items():
            setattr(ticket, key, value)
        db.commit()
        db.refresh(ticket)
    return ticket

def list_tickets(db: Session):
    return db.query(Ticket).all()

