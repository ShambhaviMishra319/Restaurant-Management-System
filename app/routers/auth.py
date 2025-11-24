from fastapi import APIRouter,Depends,HTTPException
from app import schemas
from app.database import get_db
from sqlalchemy.orm import Session
from app import models
from app.utils import hashing
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime,timedelta
from jose import jwt
from app.config import settings

router=APIRouter(prefix='/auth',tags=['Auth'])

@router.post('/register',response_model=schemas.UserResponse)
def register_user(user:schemas.UserCreate,db:Session=Depends(get_db) ):

        email=user.email
        user_found=db.query(models.User).filter(models.User.email==email).first()

        if not user_found:
            hashed_pw=hashing.hash_password(user.password)
            new_user=models.User(
                name=user.name,
                email=user.email,
                hashed_password=hashed_pw,
                role=user.role 
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        else:
            raise HTTPException(401,"user alredy there") 


    
@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user:
        raise HTTPException(401, "Invalid Credentials")

    if not hashing.verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Incorrect Password")

    token_data = {
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=12)
    }

    token = jwt.encode(token_data, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)

    return {"access_token": token, "token_type": "bearer"}


@router.get('/getUsers',response_model=list[schemas.UserResponse])
def get_all_users(db:Session=Depends(get_db)):
     all_users=db.query(models.User).all()
     return all_users