from pydantic import BaseModel
from datetime import datetime

class AttachmentCreate(BaseModel):
    ticket_id: int
    file_path: str
    uploaded_by: int

class AttachmentRead(BaseModel):
    id: int
    ticket_id: int
    file_path: str
    uploaded_by: int
    uploaded_at: datetime

    model_config = {"from_attributes": True}
