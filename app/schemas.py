# app/schemas.py

from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    is_admin: bool = False 

class UserLogin(BaseModel):
    credential: str
    password: str
