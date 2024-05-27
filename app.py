from fastapi import *
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from database import get_db_attractions
from collections import defaultdict
from starlette import status
import json

app = FastAPI()

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")
# -----------------------------------------------


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


@app.get("/api/attractions", response_model=AttractionResponse, description="取得景點資料列表")
async def get_attractions( keyword: str | None = None, page: int = Query(ge=0)):
	print(type(page))
	results = get_db_attractions(page, keyword)
	row_count = len(results) 
	# print(results)
	attractions = []
	for row in results:
		id = row["id"]
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
	

