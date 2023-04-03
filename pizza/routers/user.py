from fastapi import APIRouter,Depends,status
from  pizza.models.schemas import ShowUser,CreateUser,DisplayUser
from typing import List
from sqlalchemy.orm import Session
from pizza.models.database import get_db
from pizza.repository.user import views
import shutil

router = APIRouter(
    tags=["Users Information"],
    prefix = "/users"
)

@router.post('/create',response_model=ShowUser, status_code = status.HTTP_201_CREATED,summary="Create User Account")
def create_user(request:CreateUser,db:Session = Depends(get_db)):
    return views.create_user(request,db)

@router.get('/get_all',response_model=List[ShowUser], status_code = status.HTTP_200_OK,summary="Get All Users")
def get_all_user(db:Session = Depends(get_db)):
    return views.get_all_user(db)

@router.get('/{id}',response_model=DisplayUser, status_code = status.HTTP_200_OK,summary="Get User by Id")
def get_user(id,db:Session = Depends(get_db)):
    return views.get_user(id,db)

@router.get('/{username}',response_model=DisplayUser, status_code = status.HTTP_200_OK,summary="Get User by Username")
def get_username(username:str,db:Session = Depends(get_db)):
    return views.get_username(username,db)

