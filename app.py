from fastapi import *
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from routers import attraction_api, mrts, user, booking_attraction, order, member_page
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import requests

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
	return static_page("index.html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return static_page("attraction.html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return static_page("booking.html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return static_page("thankyou.html")
@app.get("/memberpage", include_in_schema=False)
async def thankyou(request: Request):
	return static_page("member page.html")
# -----------------------------------------------


app.include_router(attraction_api.router)
app.include_router(mrts.router)
app.include_router(user.router)
app.include_router(booking_attraction.router)
app.include_router(order.router)
app.include_router(member_page.router)


def static_page(file_name: str):
    if is_production:
        content = get_html_content(file_name)
        if content:
            print(f"Successfully loaded {file_name} from CDN")
        return HTMLResponse(content=content, status_code=200)
    else:
        path = f"./static/{file_name}"
        if os.path.exists(path):
            print(f"Serving static file from {path}")
            return FileResponse(path, media_type="text/html")
        else:
            print(f"Static file not found: {path}")
            raise HTTPException(status_code=404, detail="Page not found")



def get_html_content(file_name: str):
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