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
    async def generate_qrcode_image(cls, url: str, save_dir: str = "static/qrcode") -> Optional[str]:    
        """
        根据 URL 生成二维码图片并保存到本地

        Args:
            url (str): 二维码内容 URL
            save_dir (str): 图片保存目录，默认为 "static/qrcode"

        Returns:
            Optional[str]: 生成的图片绝对路径，如果失败则返回 None
        """
        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
            except OSError as e:
                logger.error(f"创建目录失败: {save_dir}, error: {e}")
                return None
        
        # 使用第三方 API 生成二维码 (避免引入本地图形库依赖)
        params = {"size": "300x300", "data": url}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(settings.QR_API_URL, params=params) as response:
                    if response.status == 200:
                        content = await response.read()
                        # 使用简单的文件名生成策略，避免冲突
                        filename = f"bili_qr_{int(os.times().elapsed)}.png"
                        filepath = os.path.join(save_dir, filename)
                        with open(filepath, "wb") as f:
                            f.write(content)
                        return os.path.abspath(filepath)
                    logger.error(f"生成二维码图片失败, status: {response.status}")
                    return None
            except Exception as e:
                logger.error(f"生成二维码图片异常: {e}")
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
