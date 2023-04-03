from pydantic import BaseModel,Field
from typing import List,Optional
from datetime import datetime
from enum import Enum

class Sizes(str,Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    EXTRA_LARGE = 'extra_large'

class OrderStatus(str, Enum):
    PENDING = 'pending'
    IN_TRANSIT = 'in_transit'
    DELIVERED = 'delivered'

class CreateUser(BaseModel):
    email: str
    username : str
    password : str

class ShowUser(BaseModel):
    email: str
    username : str
    class Config():
        orm_mode = True


class ShowProfile(BaseModel):
    id: int
    lastname : str
    firstname : str
    gender : str
    class Config():
        orm_mode = True

class ShowOrder(BaseModel):
    flavour : str
    quantity : int
    class Config():
        orm_mode = True

class ShowProfileImage(BaseModel):
    name : str
    class Config():
        orm_mode = True

class DisplayUser(BaseModel):
    email: str
    username : str
    is_active : bool
    is_staff : bool
    profiles : List[ShowProfile]=[]
    orders : List[ShowOrder] = []
    class Config():
        orm_mode = True

class CreateProfile(BaseModel):
    lastname : str
    firstname : str
    othername : str
    bio : str
    gender : str
    user_id : int

class DisplayProfile(BaseModel):
    lastname : str
    firstname : str
    othername : str
    gender : str
    profileimages : List[ShowProfileImage] = []
    class Config():
        orm_mode = True

class ProfileImage(BaseModel):
    id : int
    name : str
    profile_id : int

class CreateOrder(BaseModel):
    flavour : str
    quantity : int
    size : str
    order_status : str
    user_id : int

class DisplayOrder(BaseModel):
    id : int
    quantity : int
    flavour : str
    size : str
    class Config():
        orm_mode = True

class Login(BaseModel):
    username : str
    password : str
       
class Settings(BaseModel):
    authjwt_secret_key : str = "b6d504d64dd31e3d5eb1"
    authjwt_decode_algorithms : set = {"HS384","HS512"}
    #authjwt_token_location : set = {"cookies"}
    #auth_jwt_cookies_csrf_protect : bool = False

class Setting(BaseModel):
    authjwt_secret_key : str = "b6d504d64dd31e3d5eb1"
    #authjwt_decode_algorithms : set = {"HS384","HS512"}
    authjwt_token_location : set = {"cookies"}
    auth_jwt_cookies_csrf_protect : bool = False