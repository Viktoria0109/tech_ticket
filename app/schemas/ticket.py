from pydantic import BaseModel
from typing import Optional
from enum import Enum

class Priority(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    urgent = "Urgent"

class Status(str, Enum):
    new = "New"
    assigned = "Assigned"
    in_progress = "In Progress"
    resolved = "Resolved"
    closed = "Closed"

class TicketCreate(BaseModel):
    title: str
    description: str
    location: Optional[str] = None
    priority: Priority = Priority.medium

class TicketRead(BaseModel):
    id: int
    title: str
    description: str
    location: Optional[str]
    priority: Priority
    status: Status

    class Config:
        orm_mode = True

