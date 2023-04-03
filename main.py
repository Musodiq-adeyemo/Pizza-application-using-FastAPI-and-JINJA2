from fastapi import FastAPI,Request,Depends,Form,status,UploadFile,File,HTTPException
from pizza.routers import authentication
from pizza.routers import user
from pizza.routers import order
from pizza.routers import profile
from fastapi.responses import HTMLResponse,RedirectResponse,Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from datetime import timedelta
from pizza.security.hashing import Hash
from pizza.models.schemas import Setting
from pizza.models.database import User,Profile,ProfileImage,Order
from datetime import datetime
from pizza.models.database import get_db
from datetime import datetime
import shutil



app= FastAPI(
    docs_url = "/docs",
    redoc_url= "/redocs",
    title="SIRMUSO BLOGSITE API",
    description="FRAMEWORK FOR PIZZA APP",
    version="4.0",
    openapi_url="/api/v2/openapi.json"
    
)

app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(profile.router)
app.include_router(order.router)


access_token_expire =timedelta(days=30)
refresh_token_expire = timedelta(days=1)
new_access_token_expire = timedelta(days=7)
access_algorithm = "HS384"
refresh_algorithm = "HS512"

@AuthJWT.load_config
def get_config():
    return Setting()

templates = Jinja2Templates(directory="pizza/templates")
app.mount("/static",StaticFiles(directory="pizza/static"),name="static")


@app.get("/",response_class=HTMLResponse,tags=["Template"])
def home(request: Request,Authorize:AuthJWT=Depends()):
    current_user = Authorize.get_jwt_subject()
    return templates.TemplateResponse("home.html",{"request":request,"current_user":current_user})

# USER REGISTRATION
@app.get("/register",response_class=HTMLResponse,tags=["Template"])
def signup(request: Request):
    return templates.TemplateResponse("signup.html",{"request":request})

@app.post("/register",response_class=HTMLResponse,tags=["Template"])
def signup(request: Request,username:str=Form(...),email:str=Form(...),password:str=Form(...),password2:str=Form(...),db:Session = Depends(get_db)):
    user_exist = db.query(User).filter(User.username==username).first()
    email_exist = db.query(User).filter(User.email==email).first()
    errors=[]

    if email_exist:
        errors.append("Email Already Exist,Login or Change Email.")

    if user_exist:
        errors.append("Username Already Exist,Try another one.")
    
    if not email :
        errors.append("Not a proper Email")

    if password == password2 and len(password) > 7 :
        new_user = User(username=username,email=email,password=Hash.bcrypt(password))

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        redirect_url = "signin"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    
    if len(errors) > 0 :
        return templates.TemplateResponse("signup.html",{"request":request,"errors":errors})
    else:
        errors.append("Password dont match or less than 8 charaters")
        return templates.TemplateResponse("signup.html",{"request":request,"errors":errors})

#LOGIN AUTHENTICATION
@app.get("/signin",tags=["Template"])
def login(request: Request):
    return templates.TemplateResponse("signin.html",{"request":request})


@app.post("/signin",tags=["Template"])
def login(request: Request,response:Response,Authorize:AuthJWT=Depends(),username:str=Form(...),password:str=Form(...),db:Session = Depends(get_db)):
    errors = []
    user = db.query(User).filter(User.username==username).first()

    if user is None:
        errors.append("Invalid Credentials,Please check username or password")
        return templates.TemplateResponse("signin.html",{"request":request,"errors":errors})
    
    verify_password = Hash.verify_password(password,user.password)

    if (username == user.username and verify_password):
        access_token = Authorize.create_access_token(subject=user.username,expires_time=access_token_expire)
        redirect_url = "/profile_settings"
        resp = RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
        Authorize.set_access_cookies(access_token,resp)
        return resp
    else:
        errors.append("Invalid Credentials,Please check username or password")
        return templates.TemplateResponse("signin.html",{"request":request,"errors":errors})

# profile settings route
@app.get("/profile_settings",response_class=HTMLResponse,tags=["Template"])
def settings(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("settings.html",{"request":request})

@app.post("/profile_settings",response_class=HTMLResponse,tags=["Template"])
def settings(request: Request,user_id:int=Form(...),firstname:str=Form(...),lastname:str=Form(...),othername:str=Form(...),gender:str=Form(...),bio:str=Form(...), db:Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        new_profile = Profile(lastname=lastname,user_id=user_id,bio=bio,gender=gender,firstname=firstname,othername=othername)
        db.add(new_profile)
        db.commit()
        redirect_url = "/profile"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)    
    else: 
        return templates.TemplateResponse("settings.html",{"request":request,"new_user":new_profile})

#profile page
@app.get("/profile",response_class=HTMLResponse,tags=["Template"])
def dashboard(request: Request,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    current_user = Authorize.get_jwt_subject()
    users = db.query(User).all()
    profiles = db.query(Profile).all()
    images = db.query(ProfileImage).all()

    return templates.TemplateResponse("dashboard.html",{"request":request,"users":users,"profiles":profiles,'current_user':current_user,'images':images})

#update profile
@app.get("/profile/{id}",response_class=HTMLResponse,tags=["Template"])
def dashboard(request: Request,id:int,db:Session=Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    profile = db.query(Profile).filter(Profile.id == id).first()
    return templates.TemplateResponse("dashboard.html",{"request":request,"profile":profile})

@app.post("/profile/{id}",response_class=HTMLResponse,tags=["Template"])
def dashboard(request: Request, id:int,user_id:int=Form(...),firstname:str=Form(...),lastname:str=Form(...),othername:str=Form(...),gender:str=Form(...),bio:str=Form(...), db:Session = Depends(get_db)):
    try:
        update_profile = db.query(Profile).filter(Profile.id == id).first()

        update_profile.lastname = lastname,
        update_profile.firstname = firstname,
        update_profile.othername = othername,
        update_profile.bio = bio,
        update_profile.gender = gender,
        update_profile.user_id = user_id
    
        db.commit()
        redirect_url = "/profile"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    except:
        return templates.TemplateResponse("dashboard.html",{"request":request,"update_profile":update_profile})


#delete profile
@app.get("/delete_profile/{id}",response_class=HTMLResponse,tags=["Template"])
def profile_delete(request: Request,id:int,db:Session=Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
   
    delete_profile = db.query(Profile).filter(Profile.id == id).first()
    if delete_profile  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    else:
        db.delete(delete_profile)
        db.commit()
        redirect_url = "/profile_settings"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)

# profile image
@app.get("/profile_image",response_class=HTMLResponse,tags=["Template"])
def upload_pimage(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("upload_profile.html",{"request":request})

@app.post("/profile_image",response_class=HTMLResponse,tags=["Template"])
def upload_pimage(request: Request,profile_id:int=Form(...),file:UploadFile = File(...),db:Session = Depends(get_db)):
    
    with open(f"pizza/static/profileimages/{file.filename}","wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    name = file.filename
    mimetype = file.content_type

    image_upload = ProfileImage(img = file.file.read(),minetype=mimetype, name=name,profile_id=profile_id)
    db.add(image_upload)
    db.commit()
    redirect_url = "/profile"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
    
# create order route
@app.get("/create/order",response_class=HTMLResponse,tags=["Template"])
def school_info(request: Request,Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    return templates.TemplateResponse("order.html",{"request":request})

@app.post("/create/order",response_class=HTMLResponse,tags=["Template"])
def create_order(request: Request,user_id:int=Form(...),size:str=Form(...),flavour:str=Form(...),quantity:int=Form(...),order_status:str=Form(...),db:Session = Depends(get_db)):
    new_order = Order(
        quantity = quantity,
        flavour = flavour,
        size = size,
        order_status= order_status,
        user_id = user_id
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    redirect_url = "/orders/user"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)

#update order route
@app.get("/update/order/{id}",response_class=HTMLResponse,tags=["Template"])
def update_school(request: Request,id:int,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    order = db.query(Order).filter(Order.id == id).first()
    return templates.TemplateResponse("edit_order.html",{"request":request,"order":order})

@app.post("/update/order/{id}",response_class=HTMLResponse,tags=["Template"])
def update_order(request: Request,id:int,user_id:int=Form(...),size:str=Form(...),flavour:str=Form(...),quantity:int=Form(...),order_status:str=Form(...),db:Session = Depends(get_db)):
    order_update = db.query(Order).filter(Order.id == id).first()
    order_update.quantity =quantity,
    order_update.flavour = flavour,
    order_update.size = size,
    order_update.order_status = order_status,
    order_update.user_id = user_id
    db.commit()

    redirect_url = "/orders/user"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)


#delete order route
@app.get("/delete/order/{id}",response_class=HTMLResponse,tags=["Template"])
def delete_school(request: Request,id:int,db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    order = db.query(Order).filter(Order.id == id).first()

    if order  is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Resources not Found")
    else:
        db.delete(order)
        db.commit()
        redirect_url = "/orders/user"
        return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)

#Get all Orders
@app.get('/orders',response_class=HTMLResponse,tags=["Template"])
def get_orders(request: Request, db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    orders = db.query(Order).all()
    users = db.query(User).all()
    return templates.TemplateResponse("all_orders.html",{"request":request,"orders":orders,'users':users})

#Get User Orders
@app.get('/orders/user',response_class=HTMLResponse,tags=["Template"])
def get_user_orders(request: Request, db:Session = Depends(get_db),Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authorized, You need to authenticate your access token")
    orders = db.query(Order).all()
    users = db.query(User).all()
    return templates.TemplateResponse("user_orders.html",{"request":request,"orders":orders,'users':users,'current_user':current_user})

@app.get("/logout")
def logout(Authorize:AuthJWT=Depends()):
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies
    
    redirect_url = "/"
    return RedirectResponse(redirect_url,status_code=status.HTTP_303_SEE_OTHER)
