from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, hash_password
from app.models.models import User
from app.schemas.schemas import UserLogin, UserRegister, ApiResponse
import datetime

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login")
def login(creds: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=creds.email).first()
    if not user or not verify_password(creds.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    return {
        "success": True,
        "data": {
            "token": "fluxora-session-token-admin-jwt",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        },
        "meta": {"timestamp": datetime.datetime.utcnow().isoformat() + "Z"}
    }

@router.post("/register")
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(email=user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already registered with this email")
    
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        role=user_in.role or "operator"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "success": True,
        "data": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        },
        "meta": {"message": "User successfully created"}
    }

@router.get("/me")
def get_me(db: Session = Depends(get_db)):
    user = db.query(User).first()
    return {
        "success": True,
        "data": {
            "id": user.id if user else 1,
            "name": user.name if user else "Energy Director",
            "email": user.email if user else "operator@fluxora.local",
            "role": user.role if user else "operator"
        }
    }
