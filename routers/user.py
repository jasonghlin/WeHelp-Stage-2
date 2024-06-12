from fastapi import *
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from database import check_db_user, create_db_user, get_user
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from datetime import timedelta, datetime

load_dotenv(dotenv_path='../.env')

router = APIRouter(
    tags=['User']
)

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = "HS256"
# 聲明一个 OAuth2PasswordBearer 實例，指向產生 token 的 URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/auth")


class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: str

class User(BaseModel):
    name: str
    email: str
    hashed_password: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class SuccessResponse(BaseModel):
    ok: bool

class SuccessResponseToken(BaseModel):
    token: str

class ErrorResponse(BaseModel):
    error: bool
    message: str

class LoginStatusResponse(BaseModel):
    id: int
    name: str
    email: str

class LoginStatus(BaseModel):
    data: LoginStatusResponse

@router.post("/api/user", status_code=status.HTTP_200_OK, summary="註冊一個新的會員", responses={200: {"model": SuccessResponse}, 400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def create_user(create_user_request: CreateUserRequest):
    # 判斷密碼長相
    # 判斷 email 是否重複
    # 如何 email 驗證
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


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/api/user/auth", status_code=status.HTTP_200_OK, response_model = LoginStatus,  summary="取得當前登入的會員資訊")
async def get_user_status(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    # print(payload)
    return LoginStatus(data = LoginStatusResponse(id = payload.get("id"), name = payload.get("name"), email=payload.get("sub")))


def create_access_token(user_id: int, name: str, email: str, expires_delta: timedelta):
    encode = {"sub": email, "id": user_id, "name": name}
    expires = datetime.utcnow()+ expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

@router.put("/api/user/auth", status_code=status.HTTP_200_OK, summary="登入會員帳戶", responses={200: {"model": SuccessResponseToken}, 400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def login_for_access_token(user_login_request: UserLoginRequest):
    user = get_user(user_login_request)
    if not user or not bcrypt_context.verify(user_login_request.password, user.get("password")):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": True, "message": "登入失敗，帳號或密碼錯誤"}
        )
    token = create_access_token(user.get("id"), user.get("name"), user.get("email"), timedelta(days=7))
    return SuccessResponseToken(token = token)