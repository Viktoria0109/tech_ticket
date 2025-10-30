from pydantic import BaseModel
from typing import Optional
from enum import Enum

class Status(str, Enum):
    new = "New"
    assigned = "Assigned"
    in_progress = "In Progress"
    resolved = "Resolved"
    closed = "Closed"

class TicketBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Status = Status.new
    assigned_to: Optional[int] = None 

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Status] = None
    assigned_to: Optional[int] = None

class TicketRead(TicketBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


