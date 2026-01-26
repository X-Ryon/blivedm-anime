# -*- coding: utf-8 -*-
import asyncio
import blivedm
import blivedm.models.web as web_models
from typing import Dict, List, Set, Optional
from fastapi import WebSocket
from backend.app.schemas import schemas
from backend.app.crud import crud
from backend.app.database.db import AsyncSessionLocal
import aiohttp

# 身份映射
PRIVILEGE_MAP = {
    0: "普通",
    1: "总督",
    2: "提督",
    3: "舰长"
}

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
            price=0
        )
        
        print(f"房间:{self.room_id}，用户名:{message.uname}，弹幕: {message.msg}，舰队:{privilege_name}，身份:{identity}")
        asyncio.create_task(self.service.broadcast_danmaku(self.room_id, resp))
        asyncio.create_task(self._save_danmaku(message, privilege_name, identity))

    def _on_super_chat(self, client: blivedm.BLiveClient, message: web_models.SuperChatMessage):
        resp = schemas.DanmakuResponse(
            user_name=message.uname,
            level=message.medal_level if message.medal_level else 0,
            privilege_name="普通",
            dm_text=message.message,
            identity="普通",
            price=message.price
        )
        asyncio.create_task(self.service.broadcast_danmaku(self.room_id, resp))
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
            price=price
        )
        asyncio.create_task(self.service.broadcast_gift(self.room_id, resp))
        asyncio.create_task(self._save_gift(message))

    def _on_buy_guard(self, client: blivedm.BLiveClient, message: web_models.GuardBuyMessage):
        guard_name = PRIVILEGE_MAP.get(message.guard_level, "未知舰队")
        resp = schemas.GiftResponse(
            user_name=message.username,
            level=0,
            privilege_name=guard_name,
            gift_type=guard_name,
            price=float(message.price)
        )
        asyncio.create_task(self.service.broadcast_gift(self.room_id, resp))
        asyncio.create_task(self._save_guard(message, guard_name))

    async def _save_danmaku(self, message, privilege_name, identity):
        async with AsyncSessionLocal() as db:
            data = schemas.DanmakuCreate(
                room_id=self.room_id,
                user_name=message.uname,
                uid=message.uid,
                level=message.medal_level if message.medal_level else 0,
                privilege_name=privilege_name,
                dm_text=message.msg,
                identity=identity
            )
            await crud.create_danmaku(db, data)

    async def _save_super_chat(self, message):
        async with AsyncSessionLocal() as db:
            data = schemas.SuperChatCreate(
                room_id=self.room_id,
                user_name=message.uname,
                uid=message.uid,
                price=message.price,
                message=message.message
            )
            await crud.create_super_chat(db, data)

    async def _save_gift(self, message):
        async with AsyncSessionLocal() as db:
            data = schemas.GiftCreate(
                room_id=self.room_id,
                user_name=message.uname,
                uid=message.uid,
                level=message.medal_level if message.medal_level else 0,
                privilege_name="普通",
                gift_name=message.gift_name,
                gift_num=message.num,
                price=float(message.total_coin),
                currency=message.coin_type
            )
            await crud.create_gift(db, data)

    async def _save_guard(self, message, privilege_name):
        async with AsyncSessionLocal() as db:
            data = schemas.GiftCreate(
                room_id=self.room_id,
                user_name=message.username,
                uid=message.uid,
                level=0,
                privilege_name=privilege_name,
                gift_name=privilege_name,
                gift_num=message.num,
                price=float(message.price),
                currency="gold"
            )
            await crud.create_gift(db, data)

class BLiveService:
    def __init__(self):
        # room_id -> BLiveClient
        self.clients: Dict[int, blivedm.BLiveClient] = {}
        # room_id -> aiohttp.ClientSession (managed by us if sessdata is used)
        self.sessions: Dict[int, aiohttp.ClientSession] = {}
        
        # room_id -> List[WebSocket] for danmaku
        self.danmaku_connections: Dict[int, Set[WebSocket]] = {}
        # room_id -> List[WebSocket] for gift
        self.gift_connections: Dict[int, Set[WebSocket]] = {}

    async def start_listen(self, room_id: int, sessdata: Optional[str] = None):
        """
        启动监听
        :param room_id: 房间号
        :param sessdata: B站 SESSDATA Cookie，用于认证身份（如显示完整用户名、发送弹幕等）
        """
        # 如果已经运行，检查是否需要更新配置（这里简单处理：如果已运行且参数变更可能需要重启，目前仅忽略）
        if room_id in self.clients and self.clients[room_id].is_running:
            return

        session = None
        if sessdata:
            # 如果提供了 SESSDATA，创建一个带 Cookie 的会话
            cookies = {'SESSDATA': sessdata}
            session = aiohttp.ClientSession(cookies=cookies, headers={'User-Agent': blivedm.utils.USER_AGENT})
            self.sessions[room_id] = session

        client = blivedm.BLiveClient(room_id, session=session)
        handler = BilibiliHandler(room_id, self)
        client.set_handler(handler)
        self.clients[room_id] = client
        client.start()

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

    async def connect_danmaku(self, websocket: WebSocket, room_id: int, sessdata: Optional[str] = None):
        await websocket.accept()
        if room_id not in self.danmaku_connections:
            self.danmaku_connections[room_id] = set()
        self.danmaku_connections[room_id].add(websocket)
        # 自动开始监听
        await self.start_listen(room_id, sessdata)

    def disconnect_danmaku(self, websocket: WebSocket, room_id: int):
        if room_id in self.danmaku_connections:
            self.danmaku_connections[room_id].remove(websocket)

    async def connect_gift(self, websocket: WebSocket, room_id: int, sessdata: Optional[str] = None):
        await websocket.accept()
        if room_id not in self.gift_connections:
            self.gift_connections[room_id] = set()
        self.gift_connections[room_id].add(websocket)
        await self.start_listen(room_id, sessdata)

    def disconnect_gift(self, websocket: WebSocket, room_id: int):
        if room_id in self.gift_connections:
            self.gift_connections[room_id].remove(websocket)

    async def broadcast_danmaku(self, room_id: int, data: schemas.DanmakuResponse):
        print(f"Broadcasting danmaku to {room_id}, active connections: {len(self.danmaku_connections.get(room_id, []))}")
        if room_id in self.danmaku_connections:
            for connection in list(self.danmaku_connections[room_id]):
                try:
                    await connection.send_json(data.model_dump())
                except Exception as e:
                    print(f"Broadcast error: {e}")
                    self.disconnect_danmaku(connection, room_id)

    async def broadcast_gift(self, room_id: int, data: schemas.GiftResponse):
        if room_id in self.gift_connections:
            for connection in list(self.gift_connections[room_id]):
                try:
                    await connection.send_json(data.model_dump())
                except Exception:
                    self.disconnect_gift(connection, room_id)

# 全局单例
blive_service = BLiveService()
