from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime,  Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import enum


class Status(str, enum.Enum):
    new = "New"
    assigned = "Assigned"
    in_progress = "In Progress"
    resolved = "Resolved"
    closed = "Closed"

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(Status), default=Status.new)
    user_id = Column(Integer, ForeignKey("users.id")) 
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True) 
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    comments = relationship("Comment", back_populates="ticket")
    author = relationship("User", foreign_keys=[user_id])
    assignee = relationship("User", foreign_keys=[assigned_to])
    attachments = relationship("Attachment", back_populates="ticket")
