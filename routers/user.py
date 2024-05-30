from fastapi import *
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Annotated
from database import get_db_attractions, get_db_attraction_by_id, check_db_user, create_db_user
from starlette import status
from passlib.context import CryptContext

router = APIRouter(
    tags=['User']
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: str

class User(BaseModel):
    name: str
    email: str
    hashed_password: str

class SuccessResponse(BaseModel):
    ok: bool

class ErrorResponse(BaseModel):
    error: bool
    message: str

@router.post("/api/user", response_model=ErrorResponse, status_code=status.HTTP_200_OK, summary="註冊一個新的會員", responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def create_user(create_user_request: CreateUserRequest):
    # 判斷密碼長相
    # 判斷 email 是否重複
    # 如何 email 驗證
    # form data
    user_exist = check_db_user(create_user_request)
    if user_exist:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": True, "message": "此 email 已註冊過"}
        )
    else: 
        user_hash = User(
        name = create_user_request.name,
        email = create_user_request.email,
        hashed_password = bcrypt_context.hash(create_user_request.password)
    )
        create_db_user(user_hash)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"ok": True}
        )