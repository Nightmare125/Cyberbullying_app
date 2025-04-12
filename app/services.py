# app/services.py

from sqlalchemy.orm import Session
from app.db import models
from app.schemas import UserCreate
from app.auth import utils  # Make sure utils.py has hash_password, verify_password

def create_user(user: UserCreate, db: Session):
    print("🧠 Received is_admin:", user.is_admin)  # ✅ Debug

    existing = db.query(models.User).filter(
        (models.User.Username == user.username) |
        (models.User.Email == user.email)
    ).first()
    if existing:
        return None

    hashed_password = utils.hash_password(user.password)

    new_user = models.User(
        Username=user.username,
        Email=user.email,
        Password=hashed_password,
        IsAdmin=user.is_admin
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(user, db: Session):
    record = db.query(models.User).filter(
        (models.User.Username == user.credential) |
        (models.User.Email == user.credential)
    ).first()

    if not record or not utils.verify_password(user.password, record.Password):
        return False

    return record  