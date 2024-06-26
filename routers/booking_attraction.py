from fastapi import *
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from database import create_db_booking, fetch_db_user_booking, delete_db_booking, fetch_db_user_booking
from datetime import date
from routers.user import bcrypt_context, SECRET_KEY, ALGORITHM, verify_token, SuccessResponse, ErrorResponse
import json

router = APIRouter(
    tags=['Booking']
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/booking")

class AttractionBookingInfo(BaseModel):
    attractionId: int
    date: date
    time: str
    price: int



class AttractionForBookingPage(BaseModel):
    id: int
    name: str
    address: str
    image: str

class AllUserAttractionBooking(BaseModel):
    attraction: AttractionForBookingPage
    date: date
    time: str
    price: int

class AllUserAttractionBookingResponse(BaseModel):
    data: AllUserAttractionBooking

class SuccessResponse(BaseModel):
    ok: bool

class FailedResponse(BaseModel):
    error: bool
    message: str

@router.get("/api/booking")
async def get_user_booking(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    user_bookings = fetch_db_user_booking(payload.get("id"))
    responses = []
    for booking_attraction in user_bookings:
        attraction_info = AttractionForBookingPage(
            id = booking_attraction.get("attraction_id"),
            name = booking_attraction.get("name"),
            address = booking_attraction.get("address"),
            image = json.loads(booking_attraction.get("images"))[0]
            )
        response_data = AllUserAttractionBooking(
            attraction = attraction_info,
            date = booking_attraction.get("date"),
            time = booking_attraction.get("time"),
            price = booking_attraction.get("price")
        )
        response = AllUserAttractionBookingResponse(data = response_data)
        responses.append(response)
    return responses

@router.post("/api/booking", status_code=status.HTTP_200_OK, summary="建立新的預定行程", responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def create_booking_attraction(attraction_booking_info: AttractionBookingInfo, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload:
        create_result = create_db_booking(payload.get("id"), attraction_booking_info)
        if create_result:
            return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True}
        )
        else:
            return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": True, "message": "建立失敗，輸入不正確或其他原因"}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": True, "message": "未登入系統，拒絕存取"}
        )

@router.delete("/api/booking/{attraction_id}")
async def delete_booking_attraction(attraction_id: int, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload:
        delete_booking = delete_db_booking(attraction_id)
        print(delete_booking)
        if delete_booking:
            return SuccessResponse(ok = True)
        else:
            return FailedResponse(error = True, message = "資料庫操作錯誤")
    else:
        return FailedResponse(error = True, message = "資料庫操作錯誤")