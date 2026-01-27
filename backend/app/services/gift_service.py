# -*- coding: utf-8 -*-
import aiohttp
from typing import Optional, List
from backend.app.schemas import danmaku as dm_schema
from backend.app.crud.danmaku import crud_danmaku
from backend.app.crud.user import crud_user
from backend.database.db import AsyncSessionLocal
from backend.core.conf import settings
from backend.app.models import danmaku as dm_model

class GiftService:
    async def fetch_and_save(self, room_id: int, user_name: Optional[str] = None) -> List[dm_model.GiftInfoRoom]:
        url = f"{settings.BILIBILI_API_GIFT_LIST}?platform=pc&room_id={room_id}"

        cookies = None
        async with AsyncSessionLocal() as db:
            if user_name:
                user = await crud_user.get_user_by_name(db, user_name)
                if user and user.sessdata:
                    cookies = {'SESSDATA': user.sessdata}

        headers = {
            "User-Agent": settings.USER_AGENT,
            "Referer": f"https://live.bilibili.com/{room_id}",
        }

        async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
            async with session.get(url) as resp:
                data = await resp.json()
                if data.get("code") != 0:
                    raise RuntimeError(f"API错误: code={data.get('code')}, message={data.get('message')}")
                api_data = data.get("data", {})

        gifts: list[dm_schema.GiftInfoRoomCreate] = []

        gift_config = api_data.get("gift_config", {})
        
        base_list = []
        if isinstance(gift_config.get("base_config"), dict):
            base_list = gift_config.get("base_config", {}).get("list", []) or []
            
        room_list = []
        if isinstance(gift_config.get("room_config"), dict):
            room_list = gift_config.get("room_config", {}).get("list", []) or []
            
        merged = base_list + room_list

        for gift in merged:
            name = gift.get("name")
            price = float(gift.get("price", 0))
            coin_type = gift.get("coin_type") or "gold"
            img = gift.get("img_basic") or gift.get("img_dynamic") or ""
            gifts.append(dm_schema.GiftInfoRoomCreate(
                name=name, price=price, coin_type=coin_type, img=img
            ))

        async with AsyncSessionLocal() as db:
            async with db.begin():
                try:
                    saved = await crud_danmaku.replace_gift_info_room(db, gifts)
                    # Commit is handled by db.begin() context manager upon exit
                    return saved
                except Exception as e:
                    # Rollback is handled by db.begin() context manager upon exception
                    print(f"Failed to save gift info: {e}")
                    raise e

gift_service = GiftService()
