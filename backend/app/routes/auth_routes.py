from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.utils.security import (
    hash_password, verify_password, create_access_token, get_current_user
)

router = APIRouter()


class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    email = data.email.lower()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(name=data.name, email=email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "token": create_access_token(user.id),
        "user": {"id": user.id, "name": user.name, "email": user.email},
    }


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return {
        "token": create_access_token(user.id),
        "user": {"id": user.id, "name": user.name, "email": user.email},
    }


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "email": user.email}