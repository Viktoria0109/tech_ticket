from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[int] = 1  # по умолчанию — обычный пользователь

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: int

    class Config:
        orm_mode = True

