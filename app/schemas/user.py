from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[int] = 1

class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: int

    model_config = {"from_attributes": True}
