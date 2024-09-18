from fastapi import *
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from database import get_db_attractions, get_db_attraction_by_id
from starlette import status
import json
import logging
from dotenv import load_dotenv
import os
import redis

logging.basicConfig(level=logging.INFO)


load_dotenv(dotenv_path='../.env')
ENV = os.environ.get("ENVIRONMENT=", "")

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
    tags=['Attraction']
)

class Attraction(BaseModel):
	id: int
	name: str
	category: str
	description: str
	address: str
	transport: str
	mrt: str | None
	lat: float
	lng: float
	images: List[str]

class AttractionResponse(BaseModel):
	nextPage: int | None
	data: List[Attraction]

class ErrorResponse(BaseModel):
    error: bool
    message: str

class AttractionByIdResponse(BaseModel):
	data: Attraction



@router.get("/api/attractions", response_model=AttractionResponse, status_code=status.HTTP_200_OK, summary="取得景點資料列表", description="取得不同分頁的旅遊景點列表資料，也可以根據標題關鍵字、或捷運站名稱篩選")
async def get_attractions( keyword: str | None = None, page: int = Query(ge=0)):
	cache_key = f"attractions:{keyword}:{page}"
	logging.info(f"Checking cache for key: {cache_key}")
	cached_data = r.get(cache_key)
	if cached_data:
		logging.info(f"Cache hit for key: {cache_key}")
		return AttractionResponse.model_validate_json(cached_data)
	
	logging.info(f"Cache miss for key: {cache_key}, fetching from database")
	raw_results = get_db_attractions(page, keyword)
	results = raw_results["data"]
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
			mrt = row.get("mrt", None),
			lat = row["lat"],
			lng = row["lng"],
			images = json.loads(row["images"])
		)
		attractions.append(attraction)
	if raw_results["lastPage"]:
		next_page = None
	else:
		next_page = page + 1

	response = AttractionResponse(nextPage=next_page, data=attractions)
	r.set(cache_key, response.model_dump_json().encode('utf-8'), ex=3600)  # 快取 5 分鐘
	logging.info(f"Data cached with key: {cache_key}")
	
	return response
	

@router.get("/api/attraction/{attractionId}", responses={200: {"model": AttractionByIdResponse}, 400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}, status_code=status.HTTP_200_OK, summary="•根據景點編號取得景點資料")
async def get_attraction_by_id(attractionId: int):
	cache_key = f"attraction:{attractionId}"
	logging.info(f"Checking cache for key: {cache_key}")
	cached_data = r.get(cache_key)
	if cached_data:
		logging.info(f"Cache hit for key: {cache_key}")
		return AttractionByIdResponse.model_validate_json(cached_data)
	
	logging.info(f"Cache miss for key: {cache_key}, fetching from database")
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
				mrt = result.get("mrt", None),
				lat = result["lat"],
				lng = result["lng"],
				images = json.loads(result["images"])
		)
		response_data = AttractionByIdResponse(data=response)
		r.set(cache_key, response_data.model_dump_json().encode('utf-8'), ex=3600)  # 快取 1 小時
		logging.info(f"Data cached with key: {cache_key}")

		return response_data
	except Exception as e:
		logging.error(f"Error fetching attraction by ID: {e}")
		return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": True, "message": str(e)}
        )
