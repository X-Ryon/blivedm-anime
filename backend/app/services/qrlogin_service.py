# -*- coding: utf-8 -*-
import aiohttp
import os
import logging
from typing import Optional, Tuple, Dict, Any

from backend.core.conf import settings

logger = logging.getLogger(__name__)

class QrLoginService:
    """
    Bilibili 账号与登录相关服务
    提供二维码获取、登录状态轮询、用户信息获取等功能
    """

    @classmethod
    async def get_qrcode_data(cls) -> Tuple[Optional[str], Optional[str]]:
        """
        获取B站登录二维码的 URL 和 Key

        Returns:
            Tuple[Optional[str], Optional[str]]: 
                - url: 二维码内容URL (用于生成二维码图片)
                - qrcode_key: 二维码唯一标识 (用于轮询状态)
                - 如果获取失败，返回 (None, None)
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(settings.QR_GENERATE_URL, headers=settings.HEADERS) as response:
                    data = await response.json()
                    if data["code"] == 0:
                        return data["data"]["url"], data["data"]["qrcode_key"]
                    logger.error(f"获取二维码失败: {data}")
                    return None, None
            except Exception as e:
                logger.error(f"请求发生错误: {e}")
                return None, None

    @classmethod
    async def generate_qrcode_base64(cls, url: str) -> Optional[str]:    
        """
        根据 URL 生成二维码图片并返回 Base64 字符串
        """
        try:
            import qrcode
            import asyncio
            import io
            import base64

            loop = asyncio.get_running_loop()
            
            def _generate():
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Save to memory buffer
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                return f"data:image/png;base64,{img_str}"

            return await loop.run_in_executor(None, _generate)

        except Exception as e:
            logger.error(f"生成二维码Base64异常: {e}")
            return None

    @classmethod
    async def poll_status(cls, qrcode_key: str) -> Dict[str, Any]:
        """
        轮询二维码扫码登录状态

        Args:
            qrcode_key (str): 二维码唯一标识

        Returns:
            Dict[str, Any]: 包含 API 响应数据和 Cookies 的字典
                - data: B站 API 返回的原始 JSON 数据
                - cookies: 响应中的 Cookies 字典 (包含 SESSDATA)
        """
        url = f"{settings.QR_POLL_URL}?qrcode_key={qrcode_key}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=settings.HEADERS) as response:
                    data = await response.json()
                    # 提取 cookies
                    cookies = {}
                    for cookie in response.cookies.values():
                        cookies[cookie.key] = cookie.value
                    
                    return {
                        "data": data,
                        "cookies": cookies
                    }
            except Exception as e:
                logger.error(f"轮询异常: {e}")
                return {"data": {"code": -1, "message": str(e)}, "cookies": {}}

    @classmethod
    async def get_user_info_by_sessdata(cls, sessdata: str) -> Optional[Dict[str, Any]]:
        """
        通过 SESSDATA 获取当前登录用户的详细信息
        使用 B站 web-interface/nav 接口

        Args:
            sessdata (str): 用户的 SESSDATA Cookie

        Returns:
            Optional[Dict[str, Any]]: 用户信息字典，失败返回 None
                - uid: 用户 ID (str)
                - user_name: 用户名
                - face_img: 头像 URL
                - isLogin: 是否登录 (bool)
        """
        headers = settings.HEADERS.copy()
        headers["Cookie"] = f"SESSDATA={sessdata}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(settings.USER_INFO_URL, headers=headers) as response:
                    data = await response.json()
                    if data["code"] == 0:
                        user_data = data["data"]
                        return {
                            "uid": str(user_data["mid"]),
                            "user_name": user_data["uname"],
                            "face_img": user_data["face"],
                            "isLogin": user_data["isLogin"]
                        }
                    logger.error(f"获取用户信息失败: {data}")
                    return None
            except Exception as e:
                logger.error(f"获取用户信息异常: {e}")
                return None

qrlogin_service : QrLoginService = QrLoginService()
