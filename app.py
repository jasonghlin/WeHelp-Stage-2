from fastapi import *
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from routers import attraction_api, mrts, user, booking_attraction, order, member_page
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='./.env')
origins = [
    "http://localhost",
    "http://localhost:8000",

]



app = FastAPI()
ENV = os.environ.get("ENVIRONMENT", "development")
is_production = ENV == "production"
CDN_BASE_URL = "https://d3u8ez3u55dl9n.cloudfront.net"

if not is_production:
    app.mount("/static", StaticFiles(directory="static"), name="static")



app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return serve_static_page("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return serve_static_page("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return serve_static_page("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return serve_static_page("./static/thankyou.html", media_type="text/html")
@app.get("/memberpage", include_in_schema=False)
async def thankyou(request: Request):
	return serve_static_page("./static/member page.html", media_type="text/html")
# -----------------------------------------------


app.include_router(attraction_api.router)
app.include_router(mrts.router)
app.include_router(user.router)
app.include_router(booking_attraction.router)
app.include_router(order.router)
app.include_router(member_page.router)


def serve_static_page(file_name: str):
    if is_production:
        return HTMLResponse(content=get_html_content(file_name), status_code=200)
    else:
        return FileResponse(f"./static/{file_name}", media_type="text/html")


def get_html_content(file_name: str) -> str:
    if is_production:
        url = f"{CDN_BASE_URL}/{file_name}"
        response = requests.get(url)
        if response.status_code == 200:
            content = response.text.replace("/static/", f"{CDN_BASE_URL}/")

        else:
            raise HTTPException(status_code=404, detail="Page not found")
    else:
        with open(f"./static/{file_name}", "r") as file:
            content = file.read()

    return content