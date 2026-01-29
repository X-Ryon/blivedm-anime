from fastapi import APIRouter, Query, Response
import aiohttp
from loguru import logger

router = APIRouter()

@router.get("/image")
async def proxy_image(url: str = Query(..., description="Target image URL")):
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
