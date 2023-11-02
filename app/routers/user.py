from .. import models, schemas, utils
from fastapi import APIRouter, Depends, FastAPI, Response, status, HTTPException
from sqlalchemy.orm import Session
from ..database import engine, SessionLocal, get_db

router = APIRouter(
    prefix="/user", # cái này mặc định các link trong file đêu bắt đầu bằng "/user" để ta có thể bỏ từ "user" trong app.get đi
    tags=['Users']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
# email vaf password luu trong user


    #hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    
    new_user = models.User( **user.model_dump())
    db.add(new_user) # add vào database
    db.commit() # để lưu vào database
    db.refresh(new_user) # returning lại post, xem lại kết quả post

    return new_user


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"user wwith id: {id} was not found")
    
    return user