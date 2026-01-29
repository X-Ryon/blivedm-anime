# -*- coding: utf-8 -*-
import asyncio
from loguru import logger
import aiohttp
import json
from typing import Dict, Set, Optional, Union
from fastapi import WebSocket

# 使用本地 blivedm
from backend.blivedm import blivedm
from backend.blivedm.blivedm.models import web as web_models
from backend.app.schemas import danmaku as dm_schema
from backend.app.schemas import room as room_schema
from backend.app.crud.danmaku import crud_danmaku
from backend.app.crud.auth import crud_auth
from backend.app.crud.room import crud_room
from backend.database.db import AsyncSessionLocal
from backend.core.conf import settings

# 身份映射
PRIVILEGE_MAP = {
    0: "普通",
    1: "总督",
    2: "提督",
    3: "舰长"
}

class BilibiliHandler(blivedm.BaseHandler):
    """
    Bilibili 直播弹幕消息处理器
    负责处理收到的弹幕、礼物、SC 等消息，将其转换为内部 Schema 并广播/存储
    """
    def __init__(self, room_id: int, service: 'BLiveService'):
        self.room_id = room_id
        self.service = service

    def _on_danmaku(self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage):
        """
        处理普通弹幕消息
        """
        privilege_name = PRIVILEGE_MAP.get(message.privilege_type, "普通")
        identity = "房管" if message.admin else ("主播" if message.privilege_type == 1 else "普通")

        resp = dm_schema.DanmakuResponse(
            user_name=message.uname,
            level=message.medal_level if message.medal_level else 0,
            privilege_name=privilege_name,
            dm_text=message.msg,
            identity=identity,
            price=0,
            uid=str(message.uid),
            face_img=message.face,
            msg_type="danmaku"
        )
        
        logger.info(f"[弹幕]房间:{self.room_id}，用户名:{message.uname}，弹幕: {message.msg}，舰队:{privilege_name}，身份:{identity}")
        asyncio.create_task(self.service.broadcast(self.room_id, resp))
        asyncio.create_task(self._save_danmaku(message, privilege_name, identity))


    def _on_super_chat(self, client: blivedm.BLiveClient, message: web_models.SuperChatMessage):
        """
        处理 Super Chat (醒目留言) 消息
        """
        privilege_name = PRIVILEGE_MAP.get(message.privilege_type, "普通")
        identity = "房管" if message.admin else ("主播" if message.privilege_type == 1 else "普通")

        resp = dm_schema.DanmakuResponse(
            user_name=message.uname,
            level=message.medal_level if message.medal_level else 0,
            privilege_name=privilege_name,
            dm_text=message.message,
            identity=identity,
            face_img=message.face,
            price=message.price,
            uid=str(message.uid),
            msg_type="super_chat"
        )
        logger.info(f"[sc]房间:{self.room_id}，用户名:{message.uname}，sc: {message.message}，价值:{message.price}元")
        asyncio.create_task(self.service.broadcast(self.room_id, resp))
        asyncio.create_task(self._save_super_chat(message))

    def _on_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
        """
        处理礼物消息
        """
        price = float(message.total_coin)/1000.0
        
        # 修正盲盒礼物价格：盲盒礼物应显示实际获得物品的价值，而非盲盒本身的价格
        # 如果是盲盒礼物 (blind_gift 不为 None)
        if message.blind_gift is not None:
            # 优先使用 r_price (实际价值)，open_live 文档指出盲盒时这是爆出道具的价值
            # web 协议中可能在 blind_gift.gift_tip_price
            if message.r_price > 0:
                price = float(message.r_price) * message.num / 1000.0
            # 其次尝试使用 price (礼物单价)，open_live 文档指出盲盒时这也是爆出道具的价值
            elif message.price > 0:
                price = float(message.price) * message.num / 1000.0
        
        resp = dm_schema.GiftResponse(
            user_name=message.uname,
            level=message.medal_level if message.medal_level else 0,
            privilege_name="普通",
            num=message.num,
            gift_type=message.gift_name,
            price=price,
            msg_type="gift"
        )
        logger.info(f"[礼物]房间:{self.room_id}，用户名:{message.uname}，gift: {message.gift_name}，数量:{message.num}，单价:{price}元")
        asyncio.create_task(self.service.broadcast(self.room_id, resp))
        asyncio.create_task(self._save_gift(message, price))

    def _on_buy_guard(self, client: blivedm.BLiveClient, message: web_models.GuardBuyMessage):
        """
        处理上舰（购买舰长）消息
        """
        guard_name = PRIVILEGE_MAP.get(message.guard_level, "舰队")
        price=float(message.price) / 1000.0
        resp = dm_schema.GiftResponse(
            user_name=message.uname,
            level=0,
            privilege_name=guard_name,
            gift_type=guard_name,
            num=message.num,
            price=price,
            msg_type="guard"
        )
        logger.info(f"[舰队]房间:{self.room_id}，用户名:{message.uname}，舰队: {guard_name}，数量:{message.num}，单价:{price}元")
        asyncio.create_task(self.service.broadcast(self.room_id, resp))
        asyncio.create_task(self._save_guard(message, guard_name))

    def _on_user_toast_v2(self, client: blivedm.BLiveClient, message: web_models.UserToastV2Message):
        """
        处理续费舰长消息
        """
        guard_name = PRIVILEGE_MAP.get(message.guard_level, "舰队")
        price=float(message.price) / 1000.0
        resp = dm_schema.GiftResponse(
            user_name=message.uname,
            level=message.medal_level if message.medal_level else 0,
            privilege_name=guard_name,
            gift_type=guard_name,
            num=message.num,
            price=price,
            uid=str(message.uid),
            msg_type="guard"
        )
        logger.info(f"[舰队]房间:{self.room_id}，用户名:{message.uname}，舰队: {guard_name}，数量:{message.num}，单价:{price}元")
        asyncio.create_task(self.service.broadcast(self.room_id, resp))
        asyncio.create_task(self._save_guard(message, guard_name))

    async def _save_danmaku(self, message, privilege_name, identity):
        """保存弹幕到数据库"""
        async with AsyncSessionLocal() as db:
            try:
                data = dm_schema.DanmakuCreate(
                    room_id=str(self.room_id),
                    user_name=message.uname,
                    uid=str(message.uid),
                    level=message.medal_level if message.medal_level else 0,
                    privilege_name=privilege_name,
                    identity=identity,
                    face_img=message.face,
                    dm_text=message.msg
                )
                await crud_danmaku.create_danmaku(db, data)
                await db.commit()
            except Exception as e:
                await db.rollback()
                logger.error(f"保存弹幕失败: {e}")

    async def _save_super_chat(self, message):
        """保存 SC 到数据库"""
        async with AsyncSessionLocal() as db:
            try:
                data = dm_schema.SuperChatCreate(
                    room_id=str(self.room_id),
                    user_name=message.uname,
                    uid=str(message.uid),
                    level=message.medal_level if message.medal_level else 0,
                    privilege_name="普通", 
                    identity="普通", 
                    face_img=message.face,
                    sc_text=message.message,
                    price=message.price
                )
                await crud_danmaku.create_super_chat(db, data)
                await db.commit()
            except Exception as e:
                await db.rollback()
                logger.error(f"保存sc失败: {e}")

    async def _save_gift(self, message, price: float):
        """保存礼物到数据库"""
        async with AsyncSessionLocal() as db:
            try:
                data = dm_schema.GiftCreate(
                    room_id=str(self.room_id),
                    user_name=message.uname,
                    uid=str(message.uid),
                    level=message.medal_level if message.medal_level else 0,
                    privilege_name="普通",
                    identity="普通",
                    face_img=message.face,
                    gift_name=message.gift_name,
                    gift_num=message.num,
                    price=price
                )
                await crud_danmaku.create_gift(db, data)
                await db.commit()
            except Exception as e:
                await db.rollback()
                logger.error(f"保存礼物失败: {e}")

    async def _save_guard(self, message, privilege_name):
        """保存舰队信息到数据库"""
        async with AsyncSessionLocal() as db:
            try:
                level = 0
                if hasattr(message, 'medal_level') and message.medal_level:
                    level = message.medal_level
                
                face = ''
                if hasattr(message, 'face'):
                    face = message.face
                data = dm_schema.GiftCreate(
                    room_id=str(self.room_id),
                    user_name=message.username,
                    uid=str(message.uid),
                    level=level, 
                    privilege_name=privilege_name,
                    identity="普通",
                    face_img=face,
                    gift_name=privilege_name,
                    gift_num=message.num,
                    price=float(message.price) / 1000.0
                )
                await crud_danmaku.create_gift(db, data)
                await db.commit()
            except Exception as e:
                await db.rollback()
                logger.error(f"保存舰队失败: {e}")

class BLiveService:
    """
    Bilibili 直播服务管理器
    负责管理 WebSocket 连接、直播间监听客户端和房间信息
    """
    def __init__(self):
        # room_id -> BLiveClient
        self.clients: Dict[int, blivedm.BLiveClient] = {}
        # room_id -> aiohttp.ClientSession (managed by us if sessdata is used)
        self.sessions: Dict[int, aiohttp.ClientSession] = {}
        
        # room_id -> List[WebSocket] (Unified connection list)
        self.connections: Dict[int, Set[WebSocket]] = {}
        
        # 当前正在监听的房间 ID (单例模式)
        self.current_room_id: Optional[int] = None

    async def start_listen(self, room_id: int, user_name: Optional[str] = None, sessdata: Optional[str] = None):
        """
        开始监听指定直播间 (单例模式：自动停止旧房间)
        
        Args:
            room_id (int): 直播间 ID
            user_name (Optional[str]): 关联的用户名 (用于获取 SESSDATA) [DEPRECATED]
            sessdata (Optional[str]): 直接提供的 SESSDATA
        """
        # 如果请求的房间已经是当前正在监听的房间，且客户端已启动，则直接返回
        if self.current_room_id == room_id and room_id in self.clients:
            logger.info(f"已在监听房间 {room_id}")
            return

        # 如果有其他房间正在监听，先停止它
        if self.current_room_id and self.current_room_id != room_id:
            logger.info(f"切换监听房间：停止旧房间 {self.current_room_id}")
            await self.stop_listen(self.current_room_id)
            
        self.current_room_id = room_id
        logger.info(f"开始监听房间 {room_id}")
        
        final_sessdata = sessdata
        # 兼容旧逻辑，如果有 user_name 但没有 sessdata，尝试从数据库获取
        if not final_sessdata and user_name:
            async with AsyncSessionLocal() as db:
                auth = await crud_auth.get_user_by_name(db, user_name)
                if auth:
                    final_sessdata = auth.sessdata
                    logger.info(f"为用户 {user_name} 找到 SESSDATA")
                else:
                    logger.warning(f"用户 {user_name} 不存在于数据库中")

        # 如果提供了 SESSDATA，则创建 session
        session: Optional[aiohttp.ClientSession] = None
        if final_sessdata:
            # Explicitly set cookie with domain to ensure it's used correctly
            # Use SimpleCookie to set domain attribute
            from http.cookies import SimpleCookie
            cookie = SimpleCookie()
            cookie["SESSDATA"] = final_sessdata
            cookie["SESSDATA"]["domain"] = "bilibili.com"
            
            cookie_jar = aiohttp.CookieJar()
            cookie_jar.update_cookies(cookie)
            
            # Log masked sessdata for debugging
            masked_sessdata = final_sessdata[:5] + "***" + final_sessdata[-5:] if len(final_sessdata) > 10 else "***"
            logger.info(f"Using SESSDATA: {masked_sessdata}")

            session = aiohttp.ClientSession(cookie_jar=cookie_jar, headers={'User-Agent': settings.HEADERS['User-Agent']})
            self.sessions[room_id] = session
            
        client = blivedm.BLiveClient(room_id, session=session)
        handler = BilibiliHandler(room_id, self)
        client.set_handler(handler)
        self.clients[room_id] = client
        client.start()
        
        # 获取并保存房间信息
        title = await self._fetch_and_save_room_info(room_id, session)
        return title

    async def _fetch_and_save_room_info(self, room_id: int, session: Optional[aiohttp.ClientSession] = None) -> Optional[str]:
        """
        获取并保存房间信息到数据库
        Returns:
            str: 房间标题
        """
        url = f"{settings.BILIBILI_API_ROOM_INFO}?room_id={room_id}"
        
        own_session = False
        title = None
        if session is None:
            session = aiohttp.ClientSession(headers={'User-Agent': settings.HEADERS['User-Agent']})
            own_session = True
            
        try:
            async with session.get(url) as resp:
                data = await resp.json()
                if data['code'] == 0:
                    room_info = data['data']
                    title = room_info['title']
                    # get_info 接口返回的 uid 是主播 uid
                    host_uid = room_info['uid']
                    host_name = await self._fetch_user_name_by_uid(host_uid, session)
                    
                    async with AsyncSessionLocal() as db:
                        try:
                            room_data = room_schema.RoomCreate(
                                room_id=str(room_id),
                                title=title,
                                host=host_name or "Unknown"
                            )
                            await crud_room.create_or_update_room(db, room_data)
                            await db.commit()
                            logger.info(f"保存房间信息: {title}, 主播: {host_name}")
                        except Exception as e:
                            await db.rollback()
                            logger.error(f"保存房间信息失败: {e}")
        except Exception as e:
            logger.error(f"获取房间信息失败: {e}")
        finally:
            if own_session:
                await session.close()
        
        return title

    async def _fetch_user_name_by_uid(self, uid: int, session: aiohttp.ClientSession) -> str:
        """
        通过 UID 获取用户名称
        """
        # 使用直播用户接口，比主站用户接口风控更低
        url = f"{settings.BILIBILI_API_LIVE_USER_INFO}?uid={uid}"
        try:
            async with session.get(url) as resp:
                data = await resp.json()
                if data['code'] == 0:
                    return data['data']['info']['uname']
        except Exception as e:
            logger.error(f"获取主播名称失败: {e}")
        return ""

    async def stop_listen(self, room_id: int):
        """
        停止监听指定直播间，清理资源
        
        Args:
            room_id (int): 直播间 ID
        """
        if room_id in self.clients:
            await self.clients[room_id].stop_and_close()
            del self.clients[room_id]
        
        # 如果我们创建了 session，需要手动关闭
        if room_id in self.sessions:
            await self.sessions[room_id].close()
            del self.sessions[room_id]
            
        if self.current_room_id == room_id:
            self.current_room_id = None

    async def connect(self, websocket: WebSocket, room_id: int, user_name: Optional[str] = None):
        """
        建立 WebSocket 连接并自动启动监听
        
        Args:
            websocket (WebSocket): WebSocket 连接对象
            room_id (int): 直播间 ID
            user_name (Optional[str]): 关联用户名
        """
        await websocket.accept()
        if room_id not in self.connections:
            self.connections[room_id] = set()
        self.connections[room_id].add(websocket)
        # 自动开始监听
        await self.start_listen(room_id, user_name)

    def disconnect(self, websocket: WebSocket, room_id: int):
        """
        断开 WebSocket 连接
        
        Args:
            websocket (WebSocket): WebSocket 连接对象
            room_id (int): 直播间 ID
        """
        if room_id in self.connections:
            if websocket in self.connections[room_id]:
                self.connections[room_id].remove(websocket)

    async def broadcast(self, room_id: int, data: Union[dm_schema.DanmakuResponse, dm_schema.GiftResponse]):
        """
        广播消息到该房间的所有 WebSocket 连接
        
        Args:
            room_id (int): 直播间 ID
            data: 消息数据对象
        """
        if room_id in self.connections:
            for connection in list(self.connections[room_id]):
                try:
                    await connection.send_json(data.model_dump())
                except Exception as e:
                    logger.error(f"广播消息到房间 {room_id} 失败: {e}")
                    self.disconnect(connection, room_id)

# 全局单例
blive_service : BLiveService = BLiveService()
