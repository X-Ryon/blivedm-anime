from loguru import logger
import os
from typing import List
from fastapi import APIRouter, Query


from backend.app.services.auth_service import auth_service
from backend.app.services.qrlogin_service import qrlogin_service
from backend.app.services.uidinfo_service import uidinfo_service
from backend.app.schemas.auth import UserCreate, UserInfo, DeleteUserResponse
from backend.common.resp import Resp
from backend.common.exception.custom_exception import InternalServerException, NotFoundException
from backend.core.conf import settings

router = APIRouter()

@router.get("/auth/qrcode", summary="获取B站登录二维码", response_model=Resp)
async def get_login_qrcode():
    """
    获取B站登录二维码

    Description:
        获取B站扫码登录所需的URL和二维码Key，并生成二维码图片保存到服务器。

    Args:
        无

    Return:
        Resp: 包含二维码URL、Key及图片路径的响应对象

    Raises:
        InternalServerException: 获取二维码或生成图片失败时抛出
    """
    url, key = await qrlogin_service.get_qrcode_data()
    if not url or not key:
        raise InternalServerException(message="获取二维码失败")
    
    # 生成图片 Base64
    img_base64 = await qrlogin_service.generate_qrcode_base64(url)
    
    if not img_base64:
        raise InternalServerException(message="生成二维码图片失败")
    
    return Resp.success(data={
        "url": url,
        "qrcode_key": key,
        "img_base64": img_base64
    })

@router.get("/auth/poll", summary="轮询二维码登录状态", response_model=Resp)
async def poll_login_status(qrcode_key: str = Query(..., description="二维码Key")):
    """
    轮询二维码登录状态

    Description:
        根据二维码Key轮询B站登录接口，检查用户是否已扫码确认。若登录成功，自动获取用户信息并保存到数据库。

    Args:
        qrcode_key (str): 二维码唯一标识Key

    Return:
        Resp: 包含登录状态、用户信息及SESSDATA的响应对象

    Raises:
        InternalServerException: 获取状态失败或保存用户信息失败时抛出
    """
    result = await qrlogin_service.poll_status(qrcode_key)
    if not result:
        raise InternalServerException(message="获取状态失败")
        
    data = result.get("data", {})
    cookies = result.get("cookies", {})
    
    code = data.get("data", {}).get("code")
    
    if code == 0:
        # 登录成功
        logger.info("扫码登录成功，正在获取用户信息...")
        refresh_token = data["data"]["refresh_token"]
        sessdata = cookies.get("SESSDATA")
        uid = cookies.get("DedeUserID")

        if sessdata and uid:
            # 获取用户信息
            user_info = await uidinfo_service.get_user_info_by_uid(uid, cookies=cookies)
            
            if user_info:
                logger.info(f"获取用户信息成功: {user_info['user_name']} (UID: {user_info['uid']})")
                
                # 入库
                user_resp = UserInfo(
                    user_name=user_info["user_name"],
                    uid=user_info["uid"],
                    face_img=user_info["face_img"],
                    sessdata=sessdata
                )
                
                try:
                    await auth_service.create_user(user_resp)
                    logger.info("用户信息已保存到数据库")
                except Exception as e:
                    logger.error(f"保存用户信息失败: {e}")
                    raise InternalServerException(message="保存用户信息失败")
                
                return Resp.success(data={
                    "status": "success",
                    "data": user_info,
                    "sessdata": sessdata
                })
            else:
                # 获取用户信息失败，返回失败状态，触发前端重试或报错
                raise InternalServerException(message="登录成功但获取用户信息失败，请稍后重试")
        else:
            logger.warning("未在 Cookies 中找到 SESSDATA")
            raise InternalServerException(message="登录成功但未获取到有效凭证(SESSDATA)")
             
    elif code == 86101:
        return Resp.success(data={"status": "waiting", "message": "等待扫码"})
    elif code == 86090:
        return Resp.success(data={"status": "scanned", "message": "已扫码，等待确认"})
    elif code == 86038:
        return Resp.success(data={"status": "expired", "message": "二维码已过期"})
    else:
        return Resp.error(code=code, message=data.get("data", {}).get("message", "未知错误"))

@router.get("/auth/user/{uid}", summary="根据UID获取用户信息", response_model=Resp)
async def get_user_by_uid(uid: str):
    """
    根据UID获取用户信息，用于自动登录
    """
    user = await auth_service.get_user_by_uid(uid)
    if not user:
        raise NotFoundException(message="用户不存在")
        
    return Resp.success(data={
        "uid": user.uid,
        "user_name": user.user_name,
        "face_img": user.face_img,
        "sessdata": user.sessdata
    })


@router.post("/users", response_model=Resp[UserInfo])
async def create_user(request: UserCreate):
    """
    注册/更新用户信息
    通过 UID 获取 Bilibili 用户信息 (用户名和头像)，并保存到数据库
    """
    # 1. 中间件逻辑：通过 UID 获取用户信息
    user_info = await uidinfo_service.get_user_info_by_uid(request.uid)
    if not user_info:
        # 尝试通过 SESSDATA 获取 (备选方案)
        raise NotFoundException(message="无法通过 UID 获取用户信息，请检查 UID 是否有效")
        
    # 2. 构建 UserInfo 对象 (包含获取到的用户名和头像)
    user_resp = UserInfo(
        uid=request.uid,
        user_name=user_info["user_name"],
        face_img=user_info["face_img"],
        sessdata=request.sessdata
    )

    # 3. 保存到数据库
    db_user = await auth_service.create_user(user_resp)
    return Resp.success(data=db_user)

@router.delete("/users", response_model=Resp[DeleteUserResponse])
async def delete_user(user_name: str = Query(..., description="要删除的用户名")):
    """
    删除已保存的用户信息
    """
    success = await auth_service.delete_user(user_name)
    if not success:
        raise NotFoundException(message=f"用户 {user_name} 不存在")
        
    return Resp.success(data={
        "success": success,
        "message": f"用户 {user_name} 删除成功"
    })

@router.get("/users/list", response_model=Resp[List[UserInfo]])
async def get_user_list():
    """
    获取所有已保存的用户列表
    """
    users = await auth_service.get_all_users()
    # Convert to schema
    user_list = [
        UserInfo(
            uid=user.uid,
            user_name=user.user_name,
            face_img=user.face_img,
            sessdata=user.sessdata
        ) for user in users
    ]
    return Resp.success(data=user_list)

@router.delete("/users/{uid}", response_model=Resp)
async def delete_user_by_uid(uid: str):
    """
    根据UID删除用户
    """
    success = await auth_service.delete_user_by_uid(uid)
    if success:
        return Resp.success(message=f"用户UID {uid} 已删除")
    else:
        raise NotFoundException(message="用户不存在")
