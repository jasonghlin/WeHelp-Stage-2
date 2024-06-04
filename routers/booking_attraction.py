from fastapi import *
from pydantic import BaseModel
from typing import List
from database import get_db_mrts
from datetime import date

router = APIRouter(
    tags=['Booking']
)

class AttractionBookingInfo(BaseModel):
    attractionId: int
    date: date
    time: str
    price: int


@router.get("/api/booking")
async def get_booking():
    pass

@router.post("/api/booking")
async def create_booking_attraction(attraction_booking_info: AttractionBookingInfo):
    return attraction_booking_info

@router.delete("/api/booking")
async def delete_booking_attraction():
    pass