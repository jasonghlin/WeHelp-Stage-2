from fastapi import *
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from routers import attraction_api, mrts, user, booking_attraction, order

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

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


app.include_router(attraction_api.router)
app.include_router(mrts.router)
app.include_router(user.router)
app.include_router(booking_attraction.router)
app.include_router(order.router)