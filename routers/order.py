from fastapi import *
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from database import check_db_user, create_db_user, get_user
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
from datetime import timedelta, datetime
from routers.user import oauth2_scheme, bcrypt_context, SECRET_KEY, ALGORITHM
from datetime import date
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter(
    tags=['Order']
)

class Contact(BaseModel):
    name: str
    email: str
    phone: str

class Attraction(BaseModel):
    id: str
    name: str
    address: str
    image: str

class Trip(BaseModel):
    attraction: Attraction
    date: str
    time: str

class OrderDetails(BaseModel):
    price: str
    trip: List[Trip]

class Order(BaseModel):
    prime: str
    order: OrderDetails
    contact: Contact




@router.get("/api/env")
async def get_env():
    return JSONResponse({
        "APP_ID": os.getenv("APP_ID"),
        "APP_KEY": os.getenv("APP_KEY")
    })

@router.post("/api/orders")
async def create_order(order_request: Order):
    print(order_request)
    return {"ok": True}