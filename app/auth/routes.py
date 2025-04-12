# app/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db import database
from app.schemas import UserCreate, UserLogin
from app.services import create_user, authenticate_user

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(database.get_db)):
    user_created = create_user(user, db)

    if not user_created:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return {"message": "User registered successfully", "username": user.username, "is_admin": user.is_admin}

@router.post("/login")
def login(user: UserLogin, request: Request, db: Session = Depends(database.get_db)):
    valid_user = authenticate_user(user, db)
    if not valid_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    
    request.session["username"] = valid_user.Username
    request.session["is_admin"] = valid_user.IsAdmin
    return {
        "message": "Login successful",
        "username": valid_user.Username,
        "is_admin": valid_user.IsAdmin  # ✅ Properly returned from DB
        
    }