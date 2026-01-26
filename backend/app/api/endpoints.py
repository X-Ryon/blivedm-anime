# -*- coding: utf-8 -*-
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Body, BackgroundTasks, Query
from backend.app.services.blive_service import blive_service
from backend.app.schemas import schemas

router = APIRouter()

from backend.app.database.db import AsyncSessionLocal
from backend.app.crud import crud

# ----------------- 用户管理接口 -----------------

@router.post("/users")
async def create_user(user: schemas.UserCreate):
    """
    注册/更新用户信息 (用户名和 SESSDATA)
    """
    async with AsyncSessionLocal() as db:
        db_user = await crud.create_user(db, user)
        return {"message": f"User {db_user.user_name} saved successfully", "user_name": db_user.user_name}

# ----------------- WebSocket 接口 -----------------

@router.websocket("/ws/listen/{room_id}")
async def websocket_listen_endpoint(
    websocket: WebSocket, 
    room_id: int, 
    user_name: Optional[str] = Query(None, description="用户名称，用于查找数据库中的 Cookie")
):
    """
    WebSocket 端点：实时接收所有类型消息（弹幕、礼物、SC、上舰）
    """
    await blive_service.connect(websocket, room_id, user_name)
    try:
        while True:
            # 保持连接，接收客户端消息（如果有的话，比如心跳）
            await websocket.receive_text()
    except WebSocketDisconnect:
        blive_service.disconnect(websocket, room_id)

# ----------------- RESTful 控制接口 -----------------

@router.post("/listen/start")
async def start_listen(request: schemas.ListenRequest, background_tasks: BackgroundTasks):
    """
    接口: 启动监听任务 (通常由 WebSocket 自动触发，也可手动调用)
    """
    room_id_int = int(request.room_id)
    background_tasks.add_task(blive_service.start_listen, room_id_int, request.user_name)
    
    return {
        "message": f"Listening started for room {request.room_id}",
        "stream_url": f"/api/ws/listen/{request.room_id}",
        "protocol": "websocket"
    }

@router.post("/listen/stop")
async def stop_listen(request: schemas.ListenRequest):
    """
    接口: 停止监听任务
    """
    room_id_int = int(request.room_id)
    await blive_service.stop_listen(room_id_int)
    return {"message": f"Listening stopped for room {request.room_id}"}
