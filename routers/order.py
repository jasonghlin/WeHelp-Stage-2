from fastapi import *
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from database import create_db_order_contact, fetch_db_user_booking, get_db_order_info, update_db_order_contact
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
import json

load_dotenv()

router = APIRouter(
    tags=['Order']
)

class Contact(BaseModel):
    name: str
    email: EmailStr
    phone: str

class Attraction(BaseModel):
    id: int
    name: str
    address: str
    image: str

class Trip(BaseModel):
    attraction: Attraction
    date: date
    time: str

class OrderDetails(BaseModel):
    price: int
    trip: List[Trip]

class Order(BaseModel):
    prime: str
    order: OrderDetails
    contact: Contact

class Payment(BaseModel):
    status: int
    message: str

class OrderResponseDetail(BaseModel):
    number: str 
    payment: Payment

class OrderResponse(BaseModel):
    data: OrderResponseDetail

class OrderNumberResponseDetail(BaseModel):
    number: str
    price: int
    trip: List[Trip]
    contact: Contact
    status: int

class OrderNumberResponse(BaseModel):
    data: OrderNumberResponseDetail

def create_order_number(order_id):
    now = datetime.now()
    formatted_now = now.strftime("%Y%m%d%H%M%S")
    order_number = f"{formatted_now}{random.randint(0, 999999)}-{order_id}"
    return order_number
    
    
# 補 autherization
@router.post("/api/orders", status_code=status.HTTP_200_OK, responses={200: {"model": OrderResponse}, 400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}, summary="建立新的訂單，並完成付款程序")
async def create_order(order_request: Order, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload:
        user_id = payload.get("id")
        booking_info = fetch_db_user_booking(user_id)
        booking_id = [info.get("id") for info in booking_info]

        order_id = create_db_order_contact(order_number = None, price = order_request.order.price, booking_id = booking_id, user_id = user_id, contact = order_request.contact, status=None, paid = 0)
        order_number = create_order_number(order_id)
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
                "order_number": order_number,
                "cardholder": {
                    "phone_number": order_request.contact.phone,
                    "name": order_request.contact.name,
                    "email": order_request.contact.email
                    }
                }
        try:
            tappay_response = requests.post(URL, json=data, headers=headers)
            result = tappay_response.json()
            print(result)
            if result.get("status") == 0:
                db_result = update_db_order_contact(order_id, order_number, result.get("status"), paid = 1)

                if db_result:
                    return (OrderResponse(data = OrderResponseDetail(number = order_number, payment = Payment(status = result.get("status"), message = "付款成功"))))
                else: return ErrorResponse(error = True, message = f"訂單建立失敗，輸入不正確或其他原因")
            else:
                db_result = update_db_order_contact(order_id, order_number, result.get("status"), paid = 0)
                if db_result:
                    return (OrderResponse(data = OrderResponseDetail(number = order_number, payment = Payment(status = result.get("status"), message = result.get("msg")))))
                else: return ErrorResponse(error = True, message = f"訂單建立失敗，輸入不正確或其他原因")
        except Exception as e: 
            print(e)
    else:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": True, "message": "未登入系統，拒絕存取"}
        )
    

@router.get("/api/order/{orderNumber}", status_code=status.HTTP_200_OK, summary="根據訂單編號取得訂單資訊")
async def get_order_info(orderNumber: str, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload:
        trips = []
        results = get_db_order_info(1, orderNumber)
        # print(results)
        if results:
            number = results[0].get("number")
            price = results[0].get("price")
            contact = Contact(name=results[0].get("name"), email=results[0].get("email"), phone=results[0].get("phone"))
            for result in results:
                images = json.loads(result.get("images"))
                attraction = Attraction(id = result.get("attraction_id"), name = result.get("attraction_name"), address = result.get("address"), image=f"https://{images[0]}")
                trip = Trip(attraction = attraction, date=result.get("date"), time = result.get("time"))
                trips.append(trip)
            response = OrderNumberResponseDetail(number = number, price = price, trip = trips, contact = contact, status = results[0].get("status"))
            return OrderNumberResponse(data = response)
        else: 
            return ErrorResponse(error = True, message = f"找不到訂單，輸入不正確或其他原因")
    else:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": True, "message": "未登入系統，拒絕存取"}
        )


             
    