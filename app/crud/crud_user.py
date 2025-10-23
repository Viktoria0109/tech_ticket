from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from fastapi import HTTPException
from datetime import datetime
from app.models.user import User
from app.core.security import get_password_hash

def create_user(db: Session, user_data: UserCreate) -> User:
    user = User(**user_data.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()

def list_users(db: Session):
    return db.query(User).filter(User.is_deleted == False).all()

def soft_delete_user(db: Session, user_id: int, confirmed: bool = False):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not confirmed:
        raise HTTPException(status_code=400, detail="Deletion not confirmed")
    user.is_deleted = True
    user.deleted_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user

def restore_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.is_deleted:
        user.is_deleted = False
        user.deleted_at = None
        db.commit()
        db.refresh(user)
    return user


def create_user_admin(db: Session, username: str, email: str, password: str, role: str, department: str):
    hashed_pw = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_pw,
        role=role,
        department=department,
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user