# -*- coding: utf-8 -*-
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks, Query
from backend.app.services.blive_service import blive_service
from backend.app.schemas.room import ListenRequest, StartListenResponse, StopListenResponse

router = APIRouter()

# ----------------- WebSocket 接口 -----------------

@router.websocket("/ws/{room_id}")
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

@router.post("/start", response_model=StartListenResponse)
async def start_listen(request: ListenRequest):
    """
    接口: 启动监听任务 (通常由 WebSocket 自动触发，也可手动调用)
    """
    room_id_int = int(request.room_id)
    # user_name 参数已废弃，传递 None
    # 移除 BackgroundTasks，改为直接等待结果以便获取房间标题
    title = await blive_service.start_listen(room_id_int, None, request.sessdata)
    
    return {
        "message": f"开始监听房间 {request.room_id}",
        "stream_url": f"/api/ws/{request.room_id}",
        "protocol": "websocket",
        "room_title": title
    }

@router.post("/stop", response_model=StopListenResponse)
async def stop_listen():
    """
    接口: 停止当前正在监听的房间
    """
    current_room_id = blive_service.current_room_id
    if current_room_id:
        await blive_service.stop_listen(current_room_id)
        return {"message": f"停止监听房间 {current_room_id}"}
    else:
        return {"message": "当前没有正在监听的房间"}
