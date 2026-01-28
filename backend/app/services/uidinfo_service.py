# -*- coding: utf-8 -*-
import aiohttp
import os
import logging
from typing import Optional, Dict, Any

from backend.core.conf import settings

logger = logging.getLogger(__name__)

import asyncio
import random

class UidInfoService:

    @classmethod
    async def get_user_info_by_uid(cls, uid: str, cookies: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        """
        通过 UID 获取用户信息 (公开信息)
        使用 B站 space/acc/info 接口
        增加重试机制应对 -799 请求过于频繁

        Args:
            uid (str): 用户 UID
            cookies (Optional[Dict[str, str]]): 请求携带的 Cookies，用于通过风控验证

        Returns:
            Optional[Dict[str, Any]]: 用户信息字典，失败返回 None
                - uid: 用户 ID (str)
                - user_name: 用户名
                - face_img: 头像 URL
        """
        params = {"mid": uid}
        retry_count = 3
        
        # 避免同时并发请求导致风控，稍微随机等待一下
        await asyncio.sleep(random.uniform(1, 3))

        async with aiohttp.ClientSession(cookies=cookies) as session:
            for i in range(retry_count):
                try:
                    async with session.get(settings.USER_SPACE_URL, headers=settings.HEADERS, params=params) as response:
                        data = await response.json()
                        if data["code"] == 0:
                            user_data = data["data"]
                            return {
                                "uid": str(user_data["mid"]),
                                "user_name": user_data["name"],
                                "face_img": user_data["face"]
                            }
                        
                        logger.warning(f"通过UID获取用户信息失败 (尝试 {i+1}/{retry_count}): {data}")
                        
                        # 如果是 -799 请求过于频繁，则等待后重试
                        if data["code"] == -799:
                            await asyncio.sleep(random.uniform(1, 2))
                            continue
                        
                        # 其他错误直接返回 None
                        return None
                        
                except Exception as e:
                    logger.error(f"通过UID获取用户信息异常 (尝试 {i+1}/{retry_count}): {e}")
                    await asyncio.sleep(1)
        
        return None

uidinfo_service : UidInfoService = UidInfoService()
