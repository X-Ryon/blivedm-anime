# -*- coding: utf-8 -*-
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, BackgroundTasks, Query
from backend.app.services.blive_service import blive_service
from backend.app.services.user_service import user_service
from backend.app.services.gift_service import gift_service
from backend.app.schemas import user as user_schema
from backend.app.schemas import room as room_schema
from backend.app.schemas import danmaku as dm_schema

router = APIRouter()

# ----------------- 用户管理接口 -----------------

@router.post("/users", response_model=user_schema.UserResponse)
async def create_user(user: user_schema.UserCreate):
    """
    注册/更新用户信息 (用户名和 SESSDATA)
    """
    db_user = await user_service.create_user(user)
    return db_user

@router.delete("/users", response_model=user_schema.DeleteUserResponse)
async def delete_user(user_name: str = Query(..., description="要删除的用户名")):
    """
    删除已保存的用户信息
    """
    success = await user_service.delete_user(user_name)
    return {
        "success": success,
        "message": f"用户 {user_name} 删除成功" if success else f"用户 {user_name} 不存在"
    }

@router.post("/gift-info-room", response_model=dm_schema.FetchGiftInfoResponse)
async def fetch_gift_info_room(request: dm_schema.FetchGiftInfoRequest):
    room_id_int = int(request.room_id)
    gifts = await gift_service.fetch_and_save(room_id_int, request.user_name)
    return {
        "message": f"房间 {request.room_id} 礼物列表已更新",
        "count": len(gifts),
        "gifts": gifts
    }

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

@router.post("/listen/start", response_model=room_schema.StartListenResponse)
async def start_listen(request: room_schema.ListenRequest, background_tasks: BackgroundTasks):
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

@router.post("/listen/stop", response_model=room_schema.StopListenResponse)
async def stop_listen(request: room_schema.ListenRequest):
    """
    接口: 停止监听任务
    """
    room_id_int = int(request.room_id)
    await blive_service.stop_listen(room_id_int)
    return {"message": f"Listening stopped for room {request.room_id}"}
