from sqlalchemy.orm import Session
from app.models.attachment import Attachment
from app.schemas.attachment import AttachmentCreate

def create_attachment(db: Session, data: AttachmentCreate):
    attachment = Attachment(**data.dict())
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment

