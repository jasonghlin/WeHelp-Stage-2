from fastapi import *
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from database import create_db_order_contact, fetch_db_user_booking
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
from datetime import timedelta, datetime
from routers.user import oauth2_scheme, bcrypt_context, SECRET_KEY, ALGORITHM, verify_token, ErrorResponse
from datetime import date
from typing import List
from dotenv import load_dotenv
import os
import requests
import random

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

class Payment(BaseModel):
    status: int
    message: str

class OrderResponseDetail(BaseModel):
    number: int 
    payment: Payment

class OrderResponse(BaseModel):
    data: OrderResponseDetail

def create_order_number():
    return random.randint(0, 100000000)


@router.get("/api/env")
async def get_env(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload:
        return JSONResponse({
        "APP_ID": os.getenv("APP_ID"),
        "APP_KEY": os.getenv("APP_KEY")
    })
    else:
        return ErrorResponse(error = True, message = "未登入，拒絕存取")
    
    
# 補 autherization
@router.post("/api/orders")
async def create_order(order_request: Order, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload:
        order_number = create_order_number()
        URL = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
        headers = {
        "Content-Type": "application/json",
        "x-api-key": os.getenv("PARTNER_KEY")
    }
        data = {"prime": order_request.prime,
                "partner_key": os.getenv("PARTNER_KEY"),
                "merchant_id": os.getenv("TAPPAY_MERCHANT_ID"),
                "details":"TapPay Test",
                "amount": order_request.order.price,
                "cardholder": {
                    "phone_number": order_request.contact.phone,
                    "name": order_request.contact.name,
                    "email": order_request.contact.email
                    # "order_number": order_number
                    }
                }
        try:
            tappay_response = requests.post(URL, json=data, headers=headers)
            result = tappay_response.json()
            user_id = payload.get("id")
            booking_info = fetch_db_user_booking(user_id)
            booking_id = [info.get("id") for info in booking_info]
            if result.get("status") == 0:
                db_result = create_db_order_contact(order_number, result.get("status"), order_request.order.price, booking_id, user_id, order_request.contact)

                if db_result:
                    return (OrderResponse(data = OrderResponseDetail(number = order_number, payment = Payment(status = result.get("status"), message = "付款成功"))))
                else: return ErrorResponse(error = True, message = f"訂單建立失敗，輸入不正確或其他原因")
            else:
                db_result = create_db_order_contact(order_number, result.get("status"), order_request.order.price, booking_id, user_id, order_request.contact)
                if db_result:
                    return (OrderResponse(data = OrderResponseDetail(number = order_number, payment = Payment(status = result.get("status"), message = "尚未付款"))))
                else: return ErrorResponse(error = True, message = f"訂單建立失敗，輸入不正確或其他原因")
        except Exception as e: 
            print(e)
    else:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": True, "message": "未登入系統，拒絕存取"}
        )
    
    