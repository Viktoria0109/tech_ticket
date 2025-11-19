from sqlalchemy.orm import Session
from app.models.notification import Notification

def create_notification(db: Session, user_id: int, ticket_id: int, message: str):
    note = Notification(user_id=user_id, ticket_id=ticket_id, message=message)
    try:
        db.add(note)
        db.commit()
        db.refresh(note)
        return note
    except Exception:
        db.rollback()
        raise

def mark_read(db: Session, notification_id: int):
    note = db.query(Notification).filter(Notification.id == notification_id).first()
    if note:
        note.is_read = True
        try:
            db.commit()
            db.refresh(note)
        except Exception:
            db.rollback()
            raise
    return note
