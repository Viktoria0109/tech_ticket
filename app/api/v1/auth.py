from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import create_access_token, verify_password, get_password_hash, get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import Token, LoginRequest, RegisterRequest
from app.crud.crud_user import get_user_by_email, create_user


router = APIRouter()

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def api_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register", status_code=201)
async def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким email уже существует")
    # create_user expects UserCreate schema; adapt inline to avoid circular import
    created = create_user(db, type("U", (), {"name": user_data.name, "email": user_data.email, "password": user_data.password, "role": user_data.role})())
    return {"message": "Пользователь успешно создан", "user_id": created.id}