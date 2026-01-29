# -*- coding: utf-8 -*-
import aiohttp
import logging
from typing import Optional, List
from backend.app.schemas import danmaku as dm_schema
from backend.app.crud.danmaku import crud_danmaku
from backend.app.crud.auth import crud_auth
from backend.database.db import AsyncSessionLocal
from backend.core.conf import settings
from backend.app.models import danmaku as dm_model

logger = logging.getLogger(__name__)

class GiftService:
    """
    礼物服务
    负责获取和保存直播间礼物配置信息
    """
    
    async def fetch_and_save(self, room_id: int, user_name: Optional[str] = None) -> List[dm_model.GiftInfoRoom]:
        """
        获取指定直播间的礼物列表并保存到数据库

        Args:
            room_id (int): 直播间 ID
            user_name (Optional[str]): 关联的用户名 (用于获取 SESSDATA)

        Returns:
            List[dm_model.GiftInfoRoom]: 保存的礼物信息列表

        Raises:
            RuntimeError: API 请求失败或其他错误
        """
        url = f"{settings.BILIBILI_API_GIFT_LIST}?platform=pc&room_id={room_id}"

        cookies = None
        async with AsyncSessionLocal() as db:
            if user_name:
                user = await crud_auth.get_user_by_name(db, user_name)
                if user and user.sessdata:
                    cookies = {'SESSDATA': user.sessdata}

        headers = {
            "User-Agent": settings.HEADERS.get("User-Agent"),
            "Referer": f"https://live.bilibili.com/{room_id}",
        }

        try:
            async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    if data.get("code") != 0:
                        error_msg = f"API错误: code={data.get('code')}, message={data.get('message')}"
                        logger.error(error_msg)
                        raise RuntimeError(error_msg)
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

            seen_names = set()
            unique_gifts = []
            
            for gift in merged:
                name = gift.get("name")
                if name in seen_names:
                    continue
                seen_names.add(name)
                
                price = float(gift.get("price", 0))/1000.0
                coin_type = gift.get("coin_type") or "gold"
                img = gift.get("img_basic") or gift.get("img_dynamic") or ""
                unique_gifts.append(dm_schema.GiftInfoRoomCreate(
                    name=name, price=price, coin_type=coin_type, img=img
                ))

            async with AsyncSessionLocal() as db:
                async with db.begin():
                    try:
                        saved = await crud_danmaku.replace_gift_info_room(db, unique_gifts)
                        logger.info(f"成功保存 {len(saved)} 个礼物信息到数据库 (去重前 {len(merged)} 个)")
                        return saved
                    except Exception as e:
                        logger.error(f"保存礼物信息到数据库失败: {e}")
                        raise e
                        
        except Exception as e:
            logger.error(f"获取或保存礼物信息流程异常: {e}")
            raise e

gift_service : GiftService = GiftService()
