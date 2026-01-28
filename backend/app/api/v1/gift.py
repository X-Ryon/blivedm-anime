from fastapi import APIRouter
from backend.app.services.gift_service import gift_service
from backend.app.schemas import danmaku as dm_schema

router = APIRouter()

@router.post("/gift-info-room", response_model=dm_schema.FetchGiftInfoResponse)
async def fetch_gift_info_room(request: dm_schema.FetchGiftInfoRequest):
    room_id_int = int(request.room_id)
    gifts = await gift_service.fetch_and_save(room_id_int, request.user_name)
    return {
        "message": f"房间 {request.room_id} 礼物列表已更新",
        "count": len(gifts),
        "gifts": gifts
    }