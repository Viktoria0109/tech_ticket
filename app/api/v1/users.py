from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models import user
from app.core.security import get_password_hash
from app.db.session import get_db
from app import schemas
from app.crud import crud_user

def create_admin_if_not_exists():
    db: Session = SessionLocal()
    admin_email = "admin@example.com"
    existing_admin = db.query(user).filter(user.email == admin_email).first()
    if not existing_admin:
        admin = user(
            name="Admin",
            email=admin_email,
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("Администратор создан")
    else:
        print("Администратор уже существует")
    db.close()


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=schemas.UserRead)
def create_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud_user.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email уже используется")
    return crud_user.create_user(db, user_data)


@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(user_id: int, user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(crud_user.User).filter(crud_user.User.id == user_id).first()
    if not user or user.is_deleted:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, confirmed: bool = False, db: Session = Depends(get_db)):
    return crud_user.soft_delete_user(db, user_id, confirmed)