from fastapi import FastAPI, Form, HTTPException, Depends, Query
from sqlmodel import Session
from contextlib import asynccontextmanager
import bcrypt
from app.models import Users
from app.database import get_session, create_db_and_tables
from app.controller import get_user_by_username, get_current_user, logoutUser, getCustomers, addCustomerController, updateCustomerController, deleteCustomerController
from app.auth import hash_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from app.model.naivebayes import naivebayes
from app.model.extremelearningmachine import extremelearningmachine
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

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
    customers = getCustomers(page, 10)
    return {
        "data" : customers
    }

# create customers 
@app.post("/customer")
def addCustomer(
        gender: str = Form("gender"),
        ever_married: str = Form("ever_married"),
        age: int = Form("age"),
        graduated: str = Form("graduated"),
        profession: str = Form("profession"),
        spending_score: str = Form("spending_score"),
        family_size: str = Form("family_size"),
        segmentation: str = Form("segmentation"),
        currentUser: Users = Depends(get_current_user)
    ):
    
    newCustomer = addCustomerController(
        gender=gender,
        ever_married=ever_married,
        age=age,
        graduated=graduated,
        profession=profession,
        spending_score=spending_score,
        family_size=family_size,
        segmentation=segmentation
    )
    
    return {
        "status" : "success",
        "customer" : newCustomer
    }
    
# update customers
@app.put("/customer/{item_id}")
def updateCustomer(
                item_id: int, 
                gender: str = Form("gender"),
                ever_married: str = Form("ever_married"),
                age: int = Form("age"),
                graduated: str = Form("graduated"),
                profession: str = Form("profession"),
                spending_score: str = Form("spending_score"),
                family_size: str = Form("family_size"),
                segmentation: str = Form("segmentation"),
                currentUser: Users = Depends(get_current_user)
    ):
    
    isSuccess = updateCustomerController(
        item_id=item_id,
        gender=gender,
        ever_married=ever_married,
        age=age,
        graduated=graduated,
        profession=profession,
        spending_score=spending_score,
        family_size=family_size,
        segmentation=segmentation
    )
    
    return {
        "success" : isSuccess
    }

# klasifikasi
@app.post('/customer/classification/naivebayes')
def classification(
    current_user: Users = Depends(get_current_user), 
    gender: str = Form("gender"),
    ever_married: str = Form("ever_married"),
    age: int = Form("age"),
    graduated: str = Form("graduated"),
    profession: str = Form("profession"),
    spending_score: str = Form("spending_score"),
    family_size: str = Form("family_size"),
    ):
    
    message = naivebayes(
        age=age,
        gender=gender,
        ever_married=ever_married,
        graduated=graduated,
        profession=profession,
        spending_Score=spending_score,
        family_size=family_size
    )
        
    return {
        "message" : message
    }

@app.post('/customer/classification/elm')
def elm(
    current_user: Users = Depends(get_current_user), 
    gender: str = Form("gender"),
    ever_married: str = Form("ever_married"),
    age: int = Form("age"),
    graduated: str = Form("graduated"),
    profession: str = Form("profession"),
    spending_score: str = Form("spending_score"),
    family_size: str = Form("family_size"),
    ):
    
    message = extremelearningmachine(
        age=age,
        gender=gender,
        ever_married=ever_married,
        graduated=graduated,
        profession=profession,
        spending_Score=spending_score,
        family_size=family_size
    )
        
    return {
        "message" : message
    }
    
# delete customers
@app.delete('/customer/{item_id}')
def deleteCustomer(item_id: int, currentUser: Users = Depends(get_current_user)):
    
    isSuccess = deleteCustomerController(item_id)
    
    return {
        "success" : isSuccess
    }

# Untuk logout 
@app.post("/logout")
def logout(tokenData: dict = Depends(logoutUser)):
    
    return {"message": "Success"}
