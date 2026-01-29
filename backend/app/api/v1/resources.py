from fastapi import APIRouter
from backend.common.resp import Resp
import os
from pathlib import Path

router = APIRouter()

@router.get("/assets", summary="获取素材文件列表")
async def get_assets_list():
    """
    获取 frontend/src/assets 目录下的所有文件列表
    """
    try:
        # 获取项目根目录 (假设 backend 在项目根目录下一级)
        # 当前文件: backend/app/api/v1/resources.py
        # 项目根目录: backend/app/api/v1/../../../.. -> project_root
        
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent.parent # backend/app/api/v1/resources.py -> v1 -> api -> app -> backend -> root
        assets_dir = project_root / "frontend" / "src" / "assets"
        
        if not assets_dir.exists():
             # 尝试相对于工作目录查找
            cwd = Path(os.getcwd())
            assets_dir = cwd / "frontend" / "src" / "assets"
            
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
