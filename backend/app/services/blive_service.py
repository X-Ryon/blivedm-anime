# -*- coding: utf-8 -*-
import asyncio
# 使用本地 blivedm
from backend.blivedm import blivedm
from backend.blivedm.blivedm.models import web as web_models
from typing import Dict, List, Set, Optional, Union
from fastapi import WebSocket
from backend.app.schemas import schemas
from backend.app.crud.crud import crud_dao
from backend.database.db import AsyncSessionLocal
import aiohttp
from backend.core.conf import settings

# 身份映射
PRIVILEGE_MAP = {
    0: "普通",
    1: "总督",
    2: "提督",
    3: "舰长"
}

import json

class BilibiliHandler(blivedm.BaseHandler):
    def __init__(self, room_id: int, service: 'BLiveService'):
        self.room_id = room_id
        self.service = service

    def _on_danmaku(self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage):
        privilege_name = PRIVILEGE_MAP.get(message.privilege_type, "普通")
        identity = "房管" if message.admin else ("主播" if message.privilege_type == 1 else "普通")

        resp = schemas.DanmakuResponse(
            user_name=message.uname,
            level=message.medal_level if message.medal_level else 0,
            privilege_name=privilege_name,
            dm_text=message.msg,
            identity=identity,
            price=0,
            msg_type="danmaku"
        )
        
        print(f"房间:{self.room_id}，用户名:{message.uname}，弹幕: {message.msg}，舰队:{privilege_name}，身份:{identity}")
        asyncio.create_task(self.service.broadcast(self.room_id, resp))
        asyncio.create_task(self._save_danmaku(message, privilege_name, identity))
        
    # 本地 blivedm 已经修改支持解析 reply_uname，这里不再需要手动解析
    # def handle(self, client: blivedm.BLiveClient, command: dict):
    #     ...


    def _on_super_chat(self, client: blivedm.BLiveClient, message: web_models.SuperChatMessage):
        resp = schemas.DanmakuResponse(
            user_name=message.uname,
            level=message.medal_level if message.medal_level else 0,
            privilege_name="普通",
            dm_text=message.message,
            identity="普通",
            price=message.price,
            msg_type="super_chat"
        )
        asyncio.create_task(self.service.broadcast(self.room_id, resp))
        asyncio.create_task(self._save_super_chat(message))

    def _on_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
        currency = "银瓜子"
        price = float(message.total_coin)
        if message.coin_type == 'gold':
            currency = "金瓜子"
            pass

        resp = schemas.GiftResponse(
            user_name=message.uname,
            level=message.medal_level if message.medal_level else 0,
            privilege_name="普通",
            gift_type=message.gift_name,
            price=price/1000.0,
            msg_type="gift"
        )
        asyncio.create_task(self.service.broadcast(self.room_id, resp))
        asyncio.create_task(self._save_gift(message))

    def _on_buy_guard(self, client: blivedm.BLiveClient, message: web_models.GuardBuyMessage):
        guard_name = PRIVILEGE_MAP.get(message.guard_level, "未知舰队")
        resp = schemas.GiftResponse(
            user_name=message.username,
            level=0,
            privilege_name=guard_name,
            gift_type=guard_name,
            price=float(message.price) / 1000.0, # price is usually in 1000s
            msg_type="guard"
        )
        asyncio.create_task(self.service.broadcast(self.room_id, resp))
        asyncio.create_task(self._save_guard(message, guard_name))

    def _on_user_toast_v2(self, client: blivedm.BLiveClient, message: web_models.UserToastV2Message):
        guard_name = PRIVILEGE_MAP.get(message.guard_level, "未知舰队")
        resp = schemas.GiftResponse(
            user_name=message.username,
            level=message.medal_level if message.medal_level else 0,
            privilege_name=guard_name,
            gift_type=guard_name,
            price=float(message.price) / 1000.0,
            msg_type="guard"
        )
        asyncio.create_task(self.service.broadcast(self.room_id, resp))
        asyncio.create_task(self._save_guard(message, guard_name))

    async def _save_danmaku(self, message, privilege_name, identity):
        async with AsyncSessionLocal() as db:
            data = schemas.DanmakuCreate(
                room_id=str(self.room_id),
                user_name=message.uname,
                uid=str(message.uid),
                level=message.medal_level if message.medal_level else 0,
                privilege_name=privilege_name,
                identity=identity,
                dm_text=message.msg
            )
            await crud_dao.create_danmaku(db, data)

    async def _save_super_chat(self, message):
        async with AsyncSessionLocal() as db:
            data = schemas.SuperChatCreate(
                room_id=str(self.room_id),
                user_name=message.uname,
                uid=str(message.uid),
                level=message.medal_level if message.medal_level else 0,
                privilege_name="普通", # SC doesn't always carry guard info easily, defaulting
                identity="普通", # Defaulting
                sc_text=message.message,
                price=message.price
            )
            await crud_dao.create_super_chat(db, data)

    async def _save_gift(self, message):
        async with AsyncSessionLocal() as db:
            data = schemas.GiftCreate(
                room_id=str(self.room_id),
                user_name=message.uname,
                uid=str(message.uid),
                level=message.medal_level if message.medal_level else 0,
                privilege_name="普通", # Gift message might not have guard info
                identity="普通",
                gift_name=message.gift_name,
                gift_num=message.num,
                price=float(message.total_coin) / 1000.0
            )
            await crud_dao.create_gift(db, data)

    async def _save_guard(self, message, privilege_name):
        async with AsyncSessionLocal() as db:
            level = 0
            if hasattr(message, 'medal_level') and message.medal_level:
                level = message.medal_level

            data = schemas.GiftCreate(
                room_id=str(self.room_id),
                user_name=message.username,
                uid=str(message.uid),
                level=level, 
                privilege_name=privilege_name,
                identity="普通",
                gift_name=privilege_name,
                gift_num=message.num,
                price=float(message.price) / 1000.0
            )
            await crud_dao.create_gift(db, data)

class BLiveService:
    def __init__(self):
        # room_id -> BLiveClient
        self.clients: Dict[int, blivedm.BLiveClient] = {}
        # room_id -> aiohttp.ClientSession (managed by us if sessdata is used)
        self.sessions: Dict[int, aiohttp.ClientSession] = {}
        
        # room_id -> List[WebSocket] (Unified connection list)
        self.connections: Dict[int, Set[WebSocket]] = {}

    async def start_listen(self, room_id: int, user_name: Optional[str] = None):
        if room_id in self.clients:
            print(f"Already listening to room {room_id}")
            return

        print(f"Starting listen for room {room_id}")
        
        sessdata = None
        if user_name:
            async with AsyncSessionLocal() as db:
                user = await crud_dao.get_user_by_name(db, user_name)
                if user:
                    sessdata = user.sessdata
                    print(f"Found SESSDATA for user {user_name}")
                else:
                    print(f"User {user_name} not found in DB")

        # 如果提供了 SESSDATA，则创建 session
        session: Optional[aiohttp.ClientSession] = None
        if sessdata:
            cookies = {'SESSDATA': sessdata}
            session = aiohttp.ClientSession(cookies=cookies, headers={'User-Agent': settings.USER_AGENT})
            self.sessions[room_id] = session
            
        client = blivedm.BLiveClient(room_id, session=session)
        handler = BilibiliHandler(room_id, self)
        client.set_handler(handler)
        self.clients[room_id] = client
        client.start()
        
        # 异步获取并保存房间信息
        asyncio.create_task(self._fetch_and_save_room_info(room_id, session))

    async def _fetch_and_save_room_info(self, room_id: int, session: Optional[aiohttp.ClientSession] = None):
        url = f"{settings.BILIBILI_API_ROOM_INFO}?room_id={room_id}"
        
        own_session = False
        if session is None:
            session = aiohttp.ClientSession(headers={'User-Agent': settings.USER_AGENT})
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
                        room_data = schemas.RoomCreate(
                            room_id=str(room_id),
                            title=title,
                            host=host_name or "Unknown"
                        )
                        await crud_dao.create_or_update_room(db, room_data)
                        print(f"Room info saved: {title}, Host: {host_name}")
        except Exception as e:
            print(f"Failed to fetch room info: {e}")
        finally:
            if own_session:
                await session.close()

    async def _fetch_user_name_by_uid(self, uid: int, session: aiohttp.ClientSession) -> str:
        # 使用直播用户接口，比主站用户接口风控更低
        url = f"{settings.BILIBILI_API_LIVE_USER_INFO}?uid={uid}"
        try:
            async with session.get(url) as resp:
                data = await resp.json()
                if data['code'] == 0:
                    return data['data']['info']['uname']
        except Exception as e:
            print(f"Failed to fetch host name: {e}")
        return ""

    async def _fetch_and_save_user_info(self, sessdata: str):
        url = settings.BILIBILI_API_USER_INFO
        cookies = {'SESSDATA': sessdata}
        async with aiohttp.ClientSession(cookies=cookies, headers={'User-Agent': settings.USER_AGENT}) as session:
            try:
                async with session.get(url) as resp:
                    data = await resp.json()
                    if data['code'] == 0:
                        uname = data['data']['uname']
                        async with AsyncSessionLocal() as db:
                            user_data = schemas.UserCreate(
                                user_name=uname,
                                sessdata=sessdata
                            )
                            await crud_dao.create_user(db, user_data)
                            print(f"User info saved: {uname}")
            except Exception as e:
                print(f"Failed to fetch user info: {e}")

    async def stop_listen(self, room_id: int):
        """
        停止监听
        """
        if room_id in self.clients:
            await self.clients[room_id].stop_and_close()
            del self.clients[room_id]
        
        # 如果我们创建了 session，需要手动关闭
        if room_id in self.sessions:
            await self.sessions[room_id].close()
            del self.sessions[room_id]

    async def connect(self, websocket: WebSocket, room_id: int, user_name: Optional[str] = None):
        """
        建立 WebSocket 连接并启动监听
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
        """
        if room_id in self.connections:
            if websocket in self.connections[room_id]:
                self.connections[room_id].remove(websocket)

    async def broadcast(self, room_id: int, data: Union[schemas.DanmakuResponse, schemas.GiftResponse]):
        """
        广播消息到所有连接
        """
        # print(f"Broadcasting to {room_id}, active connections: {len(self.connections.get(room_id, []))}")
        if room_id in self.connections:
            for connection in list(self.connections[room_id]):
                try:
                    await connection.send_json(data.model_dump())
                except Exception as e:
                    print(f"Broadcast error: {e}")
                    self.disconnect(connection, room_id)

# 全局单例
blive_service = BLiveService()
