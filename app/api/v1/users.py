from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models import User
from app.core.security import get_password_hash

def create_admin_if_not_exists():
    db: Session = SessionLocal()
    admin_email = "admin@example.com"
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    if not existing_admin:
        admin = User(
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