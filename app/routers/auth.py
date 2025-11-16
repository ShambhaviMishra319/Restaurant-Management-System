from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from datetime import timedelta, datetime
from app.database import get_db
from app import models, schemas
from app.utils.hashing import verify_password, hash_password
from app.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register",response_model=schemas.UserResponse)
def register_user(user:schemas.UserCreate,db:Session =Depends(get_db)):
    

    already_user=db.query(models.User).filter(models.User.email==user.email).first()

    if not already_user:
        hashed_pw=hash_password(user.password)
        new_user=models.User(
            name=user.name,
            email=user.email,
            hash_password=uhashed_pw,
            role=user.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    else :
        raise HTTPException(401,"user alredy there") 
    
@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user:
        raise HTTPException(401, "Invalid Credentials")

    if not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Incorrect Password")

    token_data = {
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=12)
    }

    token = jwt.encode(token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)

    return {"access_token": token, "token_type": "bearer"}
