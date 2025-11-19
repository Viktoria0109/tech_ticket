from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from fastapi import HTTPException
from datetime import datetime
from app.core.security import get_password_hash

def create_user(db: Session, user: UserCreate):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email уже используется")
    hashed_pw = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_pw,
        role=user.role
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception:
        db.rollback()
        raise

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email, User.is_deleted == False).first()

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
    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise

def restore_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.is_deleted:
        user.is_deleted = False
        user.deleted_at = None
        try:
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            raise
    return user

def create_user_admin(db: Session, name: str, email: str, password: str, role: int = 4, department: str | None = None):
    if db.query(User).filter(User.email == email).first():
        return db.query(User).filter(User.email == email).first()
    hashed_pw = get_password_hash(password)
    user = User(
        name=name,
        email=email,
        hashed_password=hashed_pw,
        role=role,
        is_active=True,
        created_at=datetime.utcnow()
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception:
        db.rollback()
        raise