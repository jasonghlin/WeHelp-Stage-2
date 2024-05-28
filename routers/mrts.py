from fastapi import *
from pydantic import BaseModel
from typing import List
from database import get_db_mrts
from starlette import status

router = APIRouter(
    tags=['MRT Station']
)

class MRTs(BaseModel):
    data: List[str]


@router.get("/api/mrts", response_model=MRTs, status_code=status.HTTP_200_OK, summary="取得捷運站名稱列表", description="取得所有捷運站名稱列表，按照週邊景點的數量由大到小排序")
async def get_mrts():
    results = get_db_mrts()
    mrts = []
    for row in results:
        if row["mrt"] is not None:
            mrts.append(row["mrt"])
    return MRTs(data = mrts)