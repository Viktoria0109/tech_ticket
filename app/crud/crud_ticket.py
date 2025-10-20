from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate
from app.schemas.ticket import TicketCreate, TicketUpdate
from datetime import datetime



def create_ticket(db: Session, ticket: TicketCreate):
    db_ticket = Ticket(**ticket.dict())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def get_ticket_by_id(db: Session, ticket_id: int):
    return db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.is_deleted == False
    ).first()



def update_ticket(db: Session, ticket_id: int, ticket_data: TicketUpdate):
    ticket = get_ticket_by_id(db, ticket_id)
    if ticket:
        for key, value in ticket_data.dict(exclude_unset=True).items():
            setattr(ticket, key, value)
        db.commit()
        db.refresh(ticket)
    return ticket

def list_tickets(db: Session):
    return db.query(Ticket).all()

def get_filtered_tickets(db: Session, status: str = None, priority: str = None, assigned_to: int = None, q: str = None):
    query = db.query(Ticket).filter(Ticket.is_deleted == False)
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if assigned_to:
        query = query.filter(Ticket.assigned_to == assigned_to)
    if q:
        query = query.filter(Ticket.title.ilike(f"%{q}%") | Ticket.description.ilike(f"%{q}%"))
    return query.all()

def soft_delete_ticket(db: Session, ticket_id: int, confirmed: bool = False):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        return None
    if not confirmed:
        raise HTTPException(status_code=400, detail="Deletion not confirmed")
    ticket.is_deleted = True
    ticket.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket

def restore_ticket(db: Session, ticket_id: int):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket and ticket.is_deleted:
        ticket.is_deleted = False
        ticket.deleted_at = None
        db.commit()
        db.refresh(ticket)
    return ticket


