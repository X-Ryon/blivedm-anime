from typing import List
from fastapi import APIRouter, Query
from backend.common.resp import Resp
from backend.database.db import AsyncSessionLocal
from backend.app.crud.danmaku import crud_danmaku
from backend.app.schemas import danmaku as dm_schema

router = APIRouter()

@router.get("/history/danmaku", response_model=Resp[List[dm_schema.DanmakuResponse]])
async def get_danmaku_history(room_id: str = Query(..., description="房间号"), limit: int = 100):
    """
    获取最近弹幕历史

    Description:
        查询指定房间的最近弹幕记录。

    Args:
        room_id (str): 房间号
        limit (int): 返回记录数量限制，默认100

    Return:
        Resp[List[DanmakuResponse]]: 包含弹幕列表的响应对象

    Raises:
        无
    """
    async with AsyncSessionLocal() as db:
        danmakus = await crud_danmaku.get_recent_danmaku(db, room_id, limit)
        
        data = [
            dm_schema.DanmakuResponse(
                user_name=d.user_name,
                level=d.level,
                privilege_name=d.privilege_name,
                dm_text=d.dm_text,
                identity=d.identity,
                price=0,
                uid=d.uid,
                face_img=d.face_img,
                msg_type="danmaku",
                timestamp=d.create_time.timestamp() if d.create_time else 0.0
            ) for d in danmakus
        ]
        return Resp.success(data=data)

@router.get("/history/gift", response_model=Resp[List[dm_schema.GiftResponse]])
async def get_gift_history(room_id: str = Query(..., description="房间号"), limit: int = 100):
    """
    获取最近礼物历史

    Description:
        查询指定房间的最近礼物（包含上舰）记录。

    Args:
        room_id (str): 房间号
        limit (int): 返回记录数量限制，默认100

    Return:
        Resp[List[GiftResponse]]: 包含礼物列表的响应对象

    Raises:
        无
    """
    async with AsyncSessionLocal() as db:
        gifts = await crud_danmaku.get_recent_gifts(db, room_id, limit)
        
        data = [
            dm_schema.GiftResponse(
                user_name=g.user_name,
                level=g.level,
                privilege_name=g.privilege_name,
                gift_type=g.gift_name,
                num=g.gift_num,
                price=g.price,
                uid=g.uid,
                face_img=g.face_img,
                msg_type="guard" if g.gift_name in ["舰长", "提督", "总督"] else "gift",
                timestamp=g.create_time.timestamp() if g.create_time else 0.0
            ) for g in gifts
        ]
        return Resp.success(data=data)

@router.get("/history/sc", response_model=Resp[List[dm_schema.DanmakuResponse]])
async def get_sc_history(room_id: str = Query(..., description="房间号"), limit: int = 100):
    """
    获取最近SC历史

    Description:
        查询指定房间的最近Super Chat（醒目留言）记录。

    Args:
        room_id (str): 房间号
        limit (int): 返回记录数量限制，默认100

    Return:
        Resp[List[DanmakuResponse]]: 包含SC列表的响应对象

    Raises:
        无
    """
    async with AsyncSessionLocal() as db:
        scs = await crud_danmaku.get_recent_super_chats(db, room_id, limit)
        
        data = [
            dm_schema.DanmakuResponse(
                user_name=s.user_name,
                level=s.level,
                privilege_name=s.privilege_name,
                dm_text=s.sc_text,
                identity=s.identity,
                price=s.price,
                uid=s.uid,
                face_img=s.face_img,
                msg_type="super_chat",
                timestamp=s.create_time.timestamp() if s.create_time else 0.0
            ) for s in scs
        ]
        return Resp.success(data=data)
