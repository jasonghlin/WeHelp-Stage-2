from fastapi import *
from fastapi import WebSocket
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from database import create_db_booking, fetch_db_user_booking, delete_db_booking, fetch_db_user_booking
from datetime import date
from routers.user import bcrypt_context, SECRET_KEY, ALGORITHM, verify_token, SuccessResponse, ErrorResponse
import json
import logging
from dotenv import load_dotenv
import os
import redis

load_dotenv(dotenv_path='../.env')

ENV = os.environ.get("ENV", "")

REDIS_HOST = os.environ.get("REDIS_HOST", "") if ENV == "production" else "localhost"
REDIS_PORT = 6379  # 默認端口,根據你的配置可能會不同
SSL = True if ENV == "production" else False




# 創建 Redis 客戶端
try:
    # 創建 RedisCluster 客戶端
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        ssl=SSL,  # 使用 SSL/TLS
        ssl_cert_reqs=None  # 跳過 SSL 驗證
    )
    
    # 測試連接
    r.ping()
    print("成功連接到 AWS ElastiCache Redis Cluster！")
except Exception as e:
    print(f"連接失敗: {e}")

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

websocket_queue = {}
@router.websocket("/ws/booking/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    websocket_queue[user_id] = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        del websocket_queue[user_id]
    except Exception as e:
        print(f"Error in websocket connection: {e}")
        await websocket.close()


async def notify_booking_update(user_id: str):
    if user_id in websocket_queue:
        try:
            await websocket_queue[user_id].send_json({"action": "refresh_booking"})
            print(f"Sent refresh_booking message to user: {user_id}")
        except Exception as e:
            print(f"Error sending WebSocket message: {e}")

@router.get("/api/booking")
async def get_user_booking(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    cache_key = f"user:{payload.get('id')}:booking"
    cached_data = r.get(cache_key)
    if cached_data:
        logging.info(f"Cache hit for key: {cache_key}")
         # Deserialize the byte string from Redis
        data_list = json.loads(cached_data.decode('utf-8'))
        # Convert list of dictionaries to list of Pydantic models
        responses = [AllUserAttractionBookingResponse(**item) for item in data_list]
        return responses
    # else:
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
        r.set(cache_key, json.dumps([json.loads(response.json()) for response in responses]).encode('utf-8'), ex=3600)
        logging.info(f"Data cached with key: {cache_key}") 
    return responses

@router.post("/api/booking", status_code=status.HTTP_200_OK, summary="建立新的預定行程", responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def create_booking_attraction(attraction_booking_info: AttractionBookingInfo, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload:
        create_result = create_db_booking(payload.get("id"), attraction_booking_info)
        if create_result:
            await notify_booking_update(str(payload.get("id")))
            cache_key = f"user:{payload.get('id')}:booking"
            cached_data = r.get(cache_key)
            if cached_data:
                user_bookings = fetch_db_user_booking(payload.get("id"))
                responses = []
                for booking_attraction in user_bookings:
                    attraction_info = AttractionForBookingPage(
                        id=booking_attraction.get("attraction_id"),
                        name=booking_attraction.get("name"),
                        address=booking_attraction.get("address"),
                        image=json.loads(booking_attraction.get("images"))[0]
                    )
                    response_data = AllUserAttractionBooking(
                        attraction=attraction_info,
                        date=booking_attraction.get("date"),
                        time=booking_attraction.get("time"),
                        price=booking_attraction.get("price")
                    )
                    response = AllUserAttractionBookingResponse(data=response_data)
                    responses.append(response)
                # 修改處：使用 json.loads(response.json()) 來進行序列化，確保 date 類型轉換為字串
                r.set(cache_key, json.dumps([json.loads(response.json()) for response in responses]).encode('utf-8'), ex=3600)
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
        if delete_booking:
            await notify_booking_update(str(payload.get("id")))
            cache_key = f"user:{payload.get('id')}:booking"
            cached_data = r.get(cache_key)
            if cached_data:
                user_bookings = fetch_db_user_booking(payload.get("id"))
                responses = []
                for booking_attraction in user_bookings:
                    attraction_info = AttractionForBookingPage(
                        id=booking_attraction.get("attraction_id"),
                        name=booking_attraction.get("name"),
                        address=booking_attraction.get("address"),
                        image=json.loads(booking_attraction.get("images"))[0]
                    )
                    response_data = AllUserAttractionBooking(
                        attraction=attraction_info,
                        date=booking_attraction.get("date"),
                        time=booking_attraction.get("time"),
                        price=booking_attraction.get("price")
                    )
                    response = AllUserAttractionBookingResponse(data=response_data)
                    responses.append(response)
                # 修改處：使用 json.loads(response.json()) 來進行序列化，確保 date 類型轉換為字串
                r.set(cache_key, json.dumps([json.loads(response.json()) for response in responses]).encode('utf-8'), ex=3600)
            return SuccessResponse(ok = True)
        else:
            return FailedResponse(error = True, message = "資料庫操作錯誤")
    else:
        return FailedResponse(error = True, message = "資料庫操作錯誤")