from fastapi import APIRouter, UploadFile, File
from typing import List
import shutil
from backend.common.resp import Resp
from backend.core.conf import settings
import os
import subprocess
from pathlib import Path

router = APIRouter()

@router.post("/assets/upload", summary="上传素材文件")
async def upload_assets(files: List[UploadFile] = File(...)):
    """
    批量上传素材文件
    """
    try:
        assets_dir = settings.STATIC_ASSETS_DIR
        if not assets_dir.exists():
            assets_dir.mkdir(parents=True, exist_ok=True)
            
        saved_files = []
        for file in files:
            file_path = assets_dir / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(file.filename)
            
        return Resp.success(data=saved_files, message=f"成功上传 {len(saved_files)} 个文件")
    except Exception as e:
        return Resp.fail(message=f"上传失败: {str(e)}")

@router.post("/assets/open_folder", summary="打开素材文件夹")
async def open_assets_folder():
    """
    在资源管理器中打开素材文件夹
    """
    try:
        assets_dir = settings.STATIC_ASSETS_DIR
        if not assets_dir.exists():
            assets_dir.mkdir(parents=True, exist_ok=True)
            
        # 仅支持 Windows
        # 使用 explorer 命令打开文件夹，相比 os.startfile 更容易将窗口置顶
        subprocess.Popen(['explorer', str(assets_dir)])
        return Resp.success(message="已打开文件夹")
    except Exception as e:
        return Resp.fail(message=f"打开文件夹失败: {str(e)}")

@router.get("/assets", summary="获取素材文件列表")
async def get_assets_list():
    """
    获取素材文件列表

    Description:
        扫描 frontend/src/assets 目录，返回所有文件的相对路径列表。
        用于前端配置中选择本地素材文件。

    Args:
        无

    Return:
        Resp[List[str]]: 包含文件相对路径的列表

    Raises:
        Resp.fail: 目录不存在或遍历异常时返回
    """
    try:
        assets_dir = settings.STATIC_ASSETS_DIR
        
        if not assets_dir.exists():
            return Resp.fail(message="Assets directory not found")

        files = []
        for file_path in assets_dir.rglob("*"):
            if file_path.is_file():
                # 返回相对于 assets 目录的路径，或者直接返回文件名
                # 这里返回相对于 assets 的路径，并将反斜杠替换为正斜杠
                rel_path = file_path.relative_to(assets_dir).as_posix()
                files.append(rel_path)
        
        return Resp.success(data=files)

    except Exception as e:
        return Resp.fail(message=f"Failed to list assets: {str(e)}")
