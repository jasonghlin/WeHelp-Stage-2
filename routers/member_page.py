from fastapi import *
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from database import update_db_user_img, get_db_user_img
from starlette import status
from dotenv import load_dotenv
from datetime import datetime
from routers.user import oauth2_scheme, bcrypt_context, SECRET_KEY, ALGORITHM, verify_token, ErrorResponse
from datetime import date
from typing import List, Optional
from dotenv import load_dotenv
import os
import requests
import random
import json
import boto3
from botocore.exceptions import NoCredentialsError

load_dotenv()

router = APIRouter(
    tags=['Upload']
)

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
BUCKET_NAME = 'taipei-day-trip-s3-bucket'

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

@router.get("/api/upload")
async def get_img(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload:
        result = get_db_user_img(payload.get("id"))
    if result:
        print(result)
        return {"message": "File found successfully", "url": result.get("url")}

@router.post("/api/upload")
async def upload_img(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if payload:
        if file.content_type not in ["image/jpeg", "image/png"]:
            return JSONResponse(content={"message": "Invalid file type"}, status_code=400)

        file_key = file.filename

        # 檢查文件是否已存在
        try:
            s3_client.head_object(Bucket=BUCKET_NAME, Key=file_key)
            return JSONResponse(content={"message": f"File '{file_key}' already exists."}, status_code=400)
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] != '404':
                raise HTTPException(status_code=500, detail="Could not check file existence")

        try:
            # 上傳文件到 S3
            s3_client.upload_fileobj(
                file.file,
                BUCKET_NAME,
                file_key,
                ExtraArgs={'ContentType': file.content_type}
            )
            # 獲取文件的 URL
            file_url = f"https://d3u8ez3u55dl9n.cloudfront.net/{file_key}"
            update_db_user_img(payload.get("id"), file_url)
        except NoCredentialsError:
            raise HTTPException(status_code=500, detail="Credentials not available")
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=str(e))

        return {"message": "File uploaded successfully", "url": file_url}
    else:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": True, "message": "未登入系統，拒絕存取"}
        )