from fastapi import APIRouter, status,HTTPException,Depends
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from pizza.models.database import get_db
from pizza.models.schemas import CreateOrder,DisplayOrder
from pizza.repository.order import views
from typing import List

router = APIRouter(
    tags=["Orders"],
    prefix = '/order' 
)

@router.post('/create',response_model=DisplayOrder, status_code = status.HTTP_201_CREATED,summary="Place An Order")
def create_order(request:CreateOrder,db:Session = Depends(get_db),Authorize:AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return views.create_order(request,db)

@router.get('/get_all',response_model=List[DisplayOrder], status_code = status.HTTP_201_CREATED,summary="Get All Orders")
def get_all_orders(db:Session = Depends(get_db),Authorize:AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return views.get_all_orders(db)

@router.get('/{id}',response_model=DisplayOrder, status_code = status.HTTP_200_OK,summary="Retrieve An Order By Id")
def get_order(id,db:Session = Depends(get_db),Authorize:AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return views.get_order(id,db)

@router.put('/update/{id}',response_model=DisplayOrder, status_code = status.HTTP_202_ACCEPTED,summary="Update An Order By Id")
def update_order(id,request:CreateOrder,db:Session = Depends(get_db),Authorize:AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return views.update_order(id,request,db,Authorize)

@router.delete('/delete/{id}', status_code = status.HTTP_204_NO_CONTENT,summary="Delete An Order By Id")
def delete_order(id,db:Session = Depends(get_db),Authorize:AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return views.delete_order(id,db,Authorize)

@router.get('/{id}/{user_id}',response_model=DisplayOrder, status_code = status.HTTP_200_OK,summary="Get a User Specific Order")
def get_user_order_by_id(id,user_id,db:Session = Depends(get_db),Authorize:AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return views.get_user_order_by_id(id,user_id,db)


@router.get('/{user_id}',response_model=DisplayOrder, status_code = status.HTTP_200_OK,summary="Retrieve All Order By  A User")
def get_user_order(user_id,db:Session = Depends(get_db),Authorize:AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return views.get_user_order(user_id,db)

@router.put('/update/order/status/{id}',response_model=DisplayOrder, status_code = status.HTTP_202_ACCEPTED,summary="Update An Order Status")
def update_order_status(id,request:CreateOrder,db:Session = Depends(get_db),Authorize:AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return views.update_order_status(id,request,db,Authorize)