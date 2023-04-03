from fastapi import status,HTTPException,Depends
from sqlalchemy.orm import Session
from pizza.models.database import Order,get_db,User
from pizza.models.schemas import CreateOrder
from fastapi_jwt_auth import AuthJWT

def get_all_orders(db:Session=Depends(get_db)):
    orders = db.query(Order).all()
    return orders

def create_order(request:CreateOrder,db:Session=Depends(get_db)):
    new_order = Order(
        quantity = request.quantity,
        flavour = request.flavour,
        size = request.size,
        order_status= request.order_status,
        user_id = request.user_id
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order

def get_order(id:int,db:Session=Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    return order

def update_order(request:CreateOrder, id:int,db:Session=Depends(get_db),Authorize:AuthJWT = Depends()):
    
    current_user = Authorize.get_jwt_subject()
    
    user = db.query(User).filter(User.username==current_user).first()

    order_update = db.query(Order).filter(Order.id == id).first()

    order_update.quantity = request.quantity,
    order_update.flavour = request.flavour,
    order_update.size = request.size,
    order_update.order_status = request.order_status,
    order_update.user_id = request.user_id

    if order_update.user_id == user.id:
        db.commit()
        return order_update
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You are not authorized to edit this order") 
    

def delete_order(id:int,db:Session=Depends(get_db),Authorize:AuthJWT = Depends()):
    order_delete = db.query(Order).filter(Order.id == id).first()
    
    current_user = Authorize.get_jwt_subject()
    
    user = db.query(User).filter(User.username==current_user).first()

    if order_delete.user == user.id:
        db.delete(order_delete)
        db.commit()
        return f"Your Order with id {id} has been deleted Successfully"
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You are not authorized to edit this order") 
    
    

def get_user_order_by_id(id:int,user_id:int,db:Session=Depends(get_db)):
    order = db.query(Order).filter(Order.id == id,Order.user_id==user_id).all()
    #order = db.query(Order,User).filter(Order.id == id,User.id==user_id).all()

    return order

def get_user_order(user_id:str,db:Session=Depends(get_db)):
    order = db.query(Order).filter(Order.user==user_id).all()
    return order

def update_order_status(request:CreateOrder, id:int,db:Session=Depends(get_db),Authorize:AuthJWT = Depends()):
    
    current_user = Authorize.get_jwt_subject()
    
    user = db.query(User).filter(User.username==current_user).first()

    order_update = db.query(Order).filter(Order.id == id).first()

    
    order_update.order_status = request.order_status

    if order_update.user_id == user.id:
        db.commit()
        return order_update
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You are not authorized to edit this order") 
    