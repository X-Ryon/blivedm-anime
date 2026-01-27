import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.app.services.gift_service import gift_service
from backend.app.models import danmaku as dm_model

@pytest.mark.asyncio
async def test_fetch_and_save_gift_info():
    mock_response = AsyncMock()
    mock_response.__aenter__.return_value = mock_response
    mock_response.json.return_value = {
        "code": 0,
        "data": {
            "gift_config": {
                "base_config": {
                    "list": [
                        {
                            "name": "小花花",
                            "price": 100,
                            "coin_type": "gold",
                            "img_basic": "http://img"
                        }
                    ]
                },
                "room_config": {
                    "list": []
                }
            }
        }
    }

    mock_session_instance = MagicMock()
    mock_session_instance.__aenter__.return_value = mock_session_instance
    mock_session_instance.__aexit__.return_value = None
    
    mock_get_ctx = MagicMock()
    mock_get_ctx.__aenter__.return_value = mock_response
    mock_get_ctx.__aexit__.return_value = None
    mock_session_instance.get.return_value = mock_get_ctx

    # Patch the constructor of ClientSession to return our mock instance
    with patch("backend.app.services.gift_service.aiohttp.ClientSession", return_value=mock_session_instance):
        with patch("backend.app.services.gift_service.crud_danmaku") as mock_crud:

            mock_crud.replace_gift_info_room = AsyncMock(return_value=[
                dm_model.GiftInfoRoom(id=1, name="小花花", price=100.0, coin_type="gold", img="http://img")
            ])
            result = await gift_service.fetch_and_save(22625025)
            assert len(result) == 1
            assert result[0].name == "小花花"
