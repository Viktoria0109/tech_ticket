from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.db.session import get_db
from app import schemas
from app.crud import crud_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

def create_admin_if_not_exists(db: Session):
    admin_email = "admin@example.com"
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    if not existing_admin:
        admin = crud_user.create_user_admin(db, name="Admin", email=admin_email, password="admin123", role=4)
        return admin
    return existing_admin

@router.post("/", response_model=schemas.UserRead, status_code=201)
def create_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud_user.create_user(db, user_data)

@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(user_id: int, user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.is_deleted:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    for field, value in user_data.dict(exclude_unset=True).items():
        if field == "password":
            setattr(user, "hashed_password", get_password_hash(value))
        else:
            setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(user_id: int, confirmed: bool = False, db: Session = Depends(get_db)):
    return crud_user.soft_delete_user(db, user_id, confirmed)
