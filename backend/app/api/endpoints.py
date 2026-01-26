# -*- coding: utf-8 -*-
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Body, BackgroundTasks, Query
from backend.app.services.blive_service import blive_service
from backend.app.schemas import schemas

router = APIRouter()

# ----------------- WebSocket 接口 (推荐) -----------------

@router.websocket("/ws/danmaku/{room_id}")
async def websocket_danmaku_endpoint(
    websocket: WebSocket, 
    room_id: int, 
    sessdata: Optional[str] = Query(None, description="B站 SESSDATA Cookie，用于认证身份")
):
    """
    WebSocket 端点：实时接收弹幕和 SC
    """
    await blive_service.connect_danmaku(websocket, room_id, sessdata)
    try:
        while True:
            # 保持连接，接收客户端消息（如果有的话，比如心跳）
            await websocket.receive_text()
    except WebSocketDisconnect:
        blive_service.disconnect_danmaku(websocket, room_id)

@router.websocket("/ws/gift/{room_id}")
async def websocket_gift_endpoint(
    websocket: WebSocket, 
    room_id: int,
    sessdata: Optional[str] = Query(None, description="B站 SESSDATA Cookie，用于认证身份")
):
    """
    WebSocket 端点：实时接收礼物和上舰
    """
    await blive_service.connect_gift(websocket, room_id, sessdata)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        blive_service.disconnect_gift(websocket, room_id)

# ----------------- RESTful 触发接口 (兼容用户需求) -----------------
# 注意：标准的 HTTP POST 请求无法直接建立长连接推送流（除了 SSE），
# 但用户描述中希望 "POST... 响应机制: 启动后台任务或 WebSocket 连接"。
# 这里我们提供 POST 接口来显式触发监听（虽然 WebSocket 连接时会自动触发），
# 并返回一个说明，告诉客户端应该去连接哪个 WebSocket 地址。

@router.post("/listen/danmaku")
async def listen_danmaku(request: schemas.ListenRequest, background_tasks: BackgroundTasks):
    """
    接口 A: 启动弹幕监听任务
    实际数据推送建议使用 WebSocket: /api/ws/danmaku/{room_id}
    """
    room_id_int = int(request.room_id)
    # 后台启动监听
    background_tasks.add_task(blive_service.start_listen, room_id_int, request.sessdata)
    
    return {
        "message": f"Listening started for room {request.room_id}",
        "stream_url": f"/api/ws/danmaku/{request.room_id}",
        "protocol": "websocket"
    }

@router.post("/listen/danmaku/stop")
async def stop_listen_danmaku(request: schemas.ListenRequest):
    """
    接口: 停止弹幕监听任务
    """
    room_id_int = int(request.room_id)
    await blive_service.stop_listen(room_id_int)
    return {"message": f"Listening stopped for room {request.room_id}"}

@router.post("/listen/gift")
async def listen_gift(request: schemas.ListenRequest, background_tasks: BackgroundTasks):
    """
    接口 B: 启动礼物监听任务
    实际数据推送建议使用 WebSocket: /api/ws/gift/{room_id}
    """
    room_id_int = int(request.room_id)
    background_tasks.add_task(blive_service.start_listen, room_id_int, request.sessdata)
    
    return {
        "message": f"Listening started for room {request.room_id}",
        "stream_url": f"/api/ws/gift/{request.room_id}",
        "protocol": "websocket"
    }

@router.post("/listen/gift/stop")
async def stop_listen_gift(request: schemas.ListenRequest):
    """
    接口: 停止礼物监听任务
    """
    room_id_int = int(request.room_id)
    await blive_service.stop_listen(room_id_int)
    return {"message": f"Listening stopped for room {request.room_id}"}
