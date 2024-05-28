from fastapi import *
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from database import get_db_attractions, get_db_attraction_by_id
from starlette import status
import json

router = APIRouter(
    tags=['Attraction']
)

class Attraction(BaseModel):
	id: int
	name: str
	category: str
	description: str
	address: str
	transport: str
	mrt: str
	lat: float
	lng: float
	images: List[str]

class AttractionResponse(BaseModel):
	nextPage: int
	data: List[Attraction]

class ErrorResponse(BaseModel):
    error: bool
    message: str

class AttractionByIdResponse(BaseModel):
	data: Attraction



@router.get("/api/attractions", response_model=AttractionResponse, status_code=status.HTTP_200_OK, summary="取得景點資料列表", description="取得不同分頁的旅遊景點列表資料，也可以根據標題關鍵字、或捷運站名稱篩選")
async def get_attractions( keyword: str | None = None, page: int = Query(ge=0)):
	print(type(page))
	results = get_db_attractions(page, keyword)
	# row_count = len(results) 
	# print(results)
	attractions = []
	for row in results:
		attraction = Attraction(
			id = row["id"],
			name =  row["name"],
			category = row["category"],
			description = row["description"],
			address = row["address"],
			transport = row["transport"],
			mrt = row["mrt"],
			lat = row["lat"],
			lng = row["lng"],
			images = json.loads(row["images"])
		)
		attractions.append(attraction)
	next_page = page + 1
	return AttractionResponse(nextPage=next_page, data=attractions)
	

@router.get("/api/attraction/{attractionId}", responses={200: {"model": AttractionByIdResponse}, 400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}, status_code=status.HTTP_200_OK, summary="•根據景點編號取得景點資料")
async def get_attraction_by_id(attractionId: int):
	try:
		result = get_db_attraction_by_id(attractionId)
		if not result:
			return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": True, "message": "景點編號不正確"}
        )
		response = Attraction(
			id = result["id"],
				name =  result["name"],
				category = result["category"],
				description = result["description"],
				address = result["address"],
				transport = result["transport"],
				mrt = result["mrt"],
				lat = result["lat"],
				lng = result["lng"],
				images = json.loads(result["images"])
		)
		return AttractionByIdResponse(data = response)
	except Exception as e:
		return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": True, "message": str(e)}
        )
