from fastapi import APIRouter, Query
from backend.app.services.user_service import user_service
from backend.app.schemas import user as user_schema

router = APIRouter(prefix="/user", tags=["用户管理接口"])

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
