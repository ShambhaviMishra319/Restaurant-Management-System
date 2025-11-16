from fastapi.security import OAUTHPasswordBearer
from fastapi import Depends,HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from jose import jwt,JWTError
from app.config import settings
from app import models

token=OAUTHPasswordBearer(tokenURL='auth/login')

def get_current_user(token:str =Depends(token),db:Session=Depends(get_db)):
    try:
        payload=jwt.decode(token,key=settings.JWT_SECRET,algorithms=[settings.JWT_ALGO])
        user_id=payload.get("user_id")

        user=db.query(models.User).filter(models.User.id==user_id)

        if not user:
           raise HTTPException(401, "User not found")
        return user
    
    except JWTError:
        raise HTTPException(401, "Invalid token")


def require_role(*allowed_roles):
    def role_checker(user: models.User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(403, "Not allowed")
        return user
    return role_checker
