from fastapi import APIRouter, Query, Response
import aiohttp
from loguru import logger

router = APIRouter()

@router.get("/image")
async def proxy_image(url: str = Query(..., description="Target image URL")):
    """
    图片反代接口

    Description:
        代理访问 Bilibili 图片资源，通过伪造 Referer 绕过 B 站防盗链机制，解决前端加载 403 问题。

    Args:
        url (str): 目标图片 URL

    Return:
        Response: 图片文件流

    Raises:
        Response(400): URL为空时返回
        Response(status_code): 上游服务器返回非200状态码时透传
        Response(500): 内部请求异常时返回
    """
    if not url:
        return Response(status_code=400)
    
    # Simple check to avoid proxying non-Bilibili or malicious URLs if needed
    # For now, we assume it's for Bilibili avatars/assets
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com/"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                     return Response(status_code=resp.status)
                content = await resp.read()
                return Response(
                    content=content, 
                    media_type=resp.headers.get("Content-Type", "image/jpeg")
                )
    except Exception as e:
        logger.error(f"Proxy image failed: {e}")
        return Response(status_code=500)
