from fastapi import FastAPI, Form, HTTPException, Depends, Query
from sqlmodel import Session
from contextlib import asynccontextmanager
import bcrypt
from app.models import Users
from app.database import get_session, create_db_and_tables
from app.controller import get_user_by_username, get_current_user, logoutUser, getCustomers
from app.auth import hash_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
    

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# testing home
@app.get("/")
def read_root():
    return {"testing": "berhasil"}

# register
@app.post("/register")
def register(
    username: str = Form('username'),
    name: str = Form('name'),
    password: str = Form('password'),
    session: Session = Depends(get_session)
):
    
    # cek apakah username sudah ada
    existingUser = get_user_by_username(username, session)
    if existingUser:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # kalo tidak hash passwordnya
    hashedPassword = hash_password(password)
    
    # lalu buat user baru
    newUser = Users(username=username, name=name, password=hashedPassword)
    
    # tambah ke database
    session.add(newUser)
    session.commit()
    session.refresh(newUser)
    
    return {
        "status" : "success"
    }

# login
@app.post("/login")
def login(
    username: str = Form('username'),
    password: str = Form('password'),
    session: Session = Depends(get_session)
):
        
    user = get_user_by_username(username, session)
    
    # jika username tidak ada
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # jika ada maka check password
    checkPw = bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))
    
    # jika password salah
    if not checkPw:
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    # buat token JWT
    accessTokenExpires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    accessToken = create_access_token(
        data={"sub": user.username}, expires_delta=accessTokenExpires
    )
        
    return {
        "status" : "success",
        "access_token" : accessToken,
        "users" : {
            "username" : user.username,
            "name" : user.name
        }
    }
                
            
            
        
    
@app.get("/user")
def protected_route(current_user: Users = Depends(get_current_user)):
    return {"message": f"Welcome {current_user.name}!"}

# CRUD Data Customers
# get customers
@app.get("/customer")
def get_customers(current_user: Users = Depends(get_current_user), page: int = Query(default=1, gt=0)):
    customers = getCustomers(page, 15)
    return {
        "data" : customers
    }

# create customers (not finish yet)
@app.post("/customer")
def addCustomer(currentUser: Users = Depends(get_current_user)):
    return {
        "status" : "success"
    }

# Untuk logout (katanya jwt tidak bisa di destroy)
@app.post("/logout")
def logout(tokenData: dict = Depends(logoutUser)):
    
    return {"message": "Success"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


# @app.get("/tes/{tes}")
# def tes(tes: str):
#     return {"coba" : tes}

