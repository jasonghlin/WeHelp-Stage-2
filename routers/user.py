from fastapi import *
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from database import check_db_user, create_db_user, get_user, update_user_name, update_user_email, update_user_password
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import jwt
from dotenv import load_dotenv
import os
from datetime import timedelta, datetime
from typing import Optional

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

class UserInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

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
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token decode error",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/api/user/auth", status_code=status.HTTP_200_OK, response_model = LoginStatus,  summary="取得當前登入的會員資訊")
async def get_user_status(token: str = Depends(oauth2_scheme)):
    if token:
        payload = verify_token(token)
    # print(payload)
        return LoginStatus(data = LoginStatusResponse(id = payload.get("id"), name = payload.get("name"), email=payload.get("sub")))
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )


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

@router.post("/api/user/edit", status_code=status.HTTP_200_OK)
async def update_user_info(user_info: UserInfo, token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload and user_info.name:
        result = update_user_name(user_info.name, payload.get("id"))
        if result:
            token = create_access_token(user_id=payload.get("id"), email=payload.get("sub"), name=user_info.name, expires_delta=timedelta(days=7))
            return SuccessResponseToken(token = token)
    elif payload and user_info.email:
        print(user_info)
        user_exist = check_db_user(user_info)
        if user_exist:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": True, "message": "此 email 已註冊過"}
            )
        else:
            result = update_user_email(user_info.email, payload.get("id"))
            if result:
                token = create_access_token(user_id=payload.get("id"), email=user_info.email, name=payload.get("name"), expires_delta=timedelta(days=7))
                return SuccessResponseToken(token = token)
    elif payload and user_info.password:
        hashed_password = bcrypt_context.hash(user_info.password)
        result = update_user_password(hashed_password, payload.get("id"))
        if result:
            return SuccessResponse(ok=True)