from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException, Depends
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.services.blive_service import blive_service
from backend.app.schemas import schemas
from backend.app.crud import crud
from backend.database.db import get_db

router = APIRouter()

@router.websocket("/ws/listen/{room_id}")
async def websocket_listen_endpoint(
    websocket: WebSocket, 
    room_id: int, 
    user_name: Optional[str] = Query(None, description="用户名称，用于查找数据库中的 Cookie")
):
    """
    WebSocket 监听接口
    """
    await blive_service.connect(websocket, room_id, user_name)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        blive_service.disconnect(websocket, room_id)

@router.post("/listen/stop", summary="停止监听直播间")
async def stop_listen(request: schemas.ListenRequest):
    """
    停止监听指定房间
    """
    await blive_service.stop_listen(int(request.room_id))
    return {"status": "success", "message": f"Stopped listening to room {request.room_id}"}

@router.post("/users", response_model=schemas.UserResponse, summary="注册/更新用户 (SESSDATA)")
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    """
    创建或更新用户信息 (主要是 SESSDATA)
    """
    return await crud.create_user(db, user)
