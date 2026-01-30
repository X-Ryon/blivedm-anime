from fastapi import APIRouter
from backend.app.services.gift_service import gift_service
from backend.app.schemas import danmaku as dm_schema
from backend.app.crud.danmaku import crud_danmaku
from backend.database.db import AsyncSessionLocal
from typing import List
from backend.common.resp import Resp

from backend.app.models import danmaku as dm_model

router = APIRouter()

@router.post("/gift-info-room", response_model=dm_schema.FetchGiftInfoResponse)
async def fetch_gift_info_room(request: dm_schema.FetchGiftInfoRequest):
    """
    更新房间礼物列表

    Description:
        从 Bilibili API 获取指定房间的礼物列表，并保存到本地数据库。

    Args:
        request (FetchGiftInfoRequest): 包含房间号和用户名的请求体

    Return:
        FetchGiftInfoResponse: 包含更新结果和礼物列表的响应对象

    Raises:
        无
    """
    room_id_int = int(request.room_id)
    gifts = await gift_service.fetch_and_save(room_id_int, request.user_name)
    return {
        "message": f"房间 {request.room_id} 礼物列表已更新",
        "count": len(gifts),
        "gifts": gifts
    }

@router.get("/list", summary="获取所有礼物列表", response_model=Resp[List[dm_schema.GiftInfoRoomResponse]])
async def get_gift_list():
    """
    获取所有礼物列表

    Description:
        获取数据库中存储的所有礼物信息（用于映射表配置等）。
        若数据库为空，会自动插入默认模拟数据。

    Args:
        无

    Return:
        Resp[List[GiftInfoRoomResponse]]: 包含礼物信息的响应列表

    Raises:
        无
    """
    async with AsyncSessionLocal() as db:
        gifts = await crud_danmaku.get_all_gift_info_room(db)
        
        # 如果数据库为空，插入一些模拟数据以便测试
        if not gifts:
            mock_gifts = [
                dm_model.GiftInfoRoom(name="情书", price=5.2, coin_type="gold", img="https://s1.hdslb.com/bfs/live/8e9f5e7c8e5c8e5c8e5c8e5c8e5c8e5c.png"), # 假图片
                dm_model.GiftInfoRoom(name="牛哇牛哇", price=6.6, coin_type="gold", img="https://s1.hdslb.com/bfs/live/8e9f5e7c8e5c8e5c8e5c8e5c8e5c8e5c.png"),
                dm_model.GiftInfoRoom(name="告白气球", price=52.0, coin_type="gold", img="https://s1.hdslb.com/bfs/live/8e9f5e7c8e5c8e5c8e5c8e5c8e5c8e5c.png"),
                dm_model.GiftInfoRoom(name="小花花", price=0.1, coin_type="silver", img="https://s1.hdslb.com/bfs/live/8e9f5e7c8e5c8e5c8e5c8e5c8e5c8e5c.png"),
            ]
            db.add_all(mock_gifts)
            await db.commit()
            
            # 重新获取
            gifts = await crud_danmaku.get_all_gift_info_room(db)

        # 手动转换为 Pydantic 模型，确保序列化正确
        data = [dm_schema.GiftInfoRoomResponse.model_validate(g) for g in gifts]
        return Resp.success(data=data)