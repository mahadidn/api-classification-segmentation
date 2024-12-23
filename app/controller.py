# app/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select, create_engine
from .database import get_session, DATABASE_URL
from .models import Users, Data_customers
from .auth import decode_access_token, SECRET_KEY, ALGORITHM_SECURE
from datetime import datetime ,timedelta
from jose import JWTError, jwt
from sqlalchemy import func

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
engine = create_engine(DATABASE_URL, echo=True)

# get user by username
def get_user_by_username(username: str, session: Session):
    statement = select(Users).where(Users.username == username)
    user = session.exec(statement).first()
    return user

# get user saat ini dari token
def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        username = decode_access_token(token)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_username(username, session)
    if user is None:
        raise credentials_exception
    return user

# get data customers
def getCustomers(page: int, size: int):
    with Session(engine) as session:
    
        offset = (page - 1) * size
        
        statement = select(Data_customers).offset(offset).limit(size)
        dataCustomers = session.exec(statement).all()
        # totalData = session.exec(select(Data_customers)).count()
        total_statement = select(func.count()).select_from(Data_customers)
        total = session.exec(total_statement).one()  # Ambil hasil tunggal
        
        return {
            "page" : page,
            "size" : size,
            "total" : total,
            "data" : dataCustomers
            
        }
# add customer 
def addCustomerController(gender: str, ever_married: str, age: int, graduated: str, profession: str, spending_score: str, family_size: str, segmentation: str):
    with Session(engine) as session:
        newCustomer = Data_customers(gender=gender, ever_married=ever_married, age=age, graduated=graduated, profession=profession, spending_score=spending_score, family_size=family_size, segmentation=segmentation)
        session.add(newCustomer)
        session.commit()
        session.refresh(newCustomer)
        
        return newCustomer

# update customer
def updateCustomerController(item_id: int, gender: str, ever_married: str, age: int, graduated: str, profession: str, spending_score: str, family_size: str, segmentation: str):
    with Session(engine) as session:
        
        statement = select(Data_customers).where(Data_customers.id == item_id)
        dataCustomer = session.exec(statement).first()
        
        if not dataCustomer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail= "Data tidak ditemukan"
            )
        
        dataCustomer.gender = gender
        dataCustomer.ever_married = ever_married
        dataCustomer.age = age
        dataCustomer.graduated = graduated
        dataCustomer.profession = profession
        dataCustomer.spending_score = spending_score
        dataCustomer.family_size = family_size
        dataCustomer.segmentation = segmentation
        
        session.add(dataCustomer)
        session.commit()
        session.refresh(dataCustomer)
        
        return True
        
# delete customer
def deleteCustomerController(item_id: int):
    with Session(engine) as session:
        statement = select(Data_customers).where(Data_customers.id == item_id)
        dataCustomer = session.exec(statement).first()
        
        if not dataCustomer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail= "Data tidak ditemukan"
            )
        
        # hapus data dari database
        session.delete(dataCustomer)
        session.commit()
        
        return True

def logoutUser(token: str = Depends(oauth2_scheme)):
    """
    Logout dengan membuat token yang dikirim tidak valid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM_SECURE])
        payload["exp"] = datetime.utcnow() - timedelta(seconds=1)  # Set waktu kadaluarsa ke masa lalu
        expired_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM_SECURE)
        return {"message": "Logged out", "expired_token": expired_token}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token already expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    