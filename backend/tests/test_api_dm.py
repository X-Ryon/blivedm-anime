import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from backend.main import app
from backend.core.conf import settings
from backend.app.models import danmaku as dm_model

# Use TestClient with a context manager to handle startup/shutdown events if needed
# But for simple tests, client = TestClient(app) is usually enough.
# However, if startup event connects to DB, we might want to mock that too to avoid side effects.
# But here we are patching the service, so the DB connection in startup might still happen but won't be used by the endpoint.

client = TestClient(app)

def test_delete_user_endpoint():
    # Patch the user_service.delete_user method where it is used in the api module
    with patch("backend.app.api.v1.dm.user_service.delete_user", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = True
        
        url = f"{settings.API_V1_PATH}/users"
        
        # Test success case
        response = client.delete(url, params={"user_name": "test_user"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "删除成功" in data["message"]
        mock_delete.assert_called_with("test_user")

        # Test failure case
        mock_delete.return_value = False
        response = client.delete(url, params={"user_name": "unknown_user"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "不存在" in data["message"]

def test_fetch_gift_info_room_endpoint():
    with patch("backend.app.api.v1.dm.gift_service.fetch_and_save", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = [
            dm_model.GiftInfoRoom(id=1, name="小花花", price=100.0, coin_type="gold", img="http://img"),
            dm_model.GiftInfoRoom(id=2, name="辣条", price=10.0, coin_type="silver", img="http://img2"),
        ]
        url = f"{settings.API_V1_PATH}/gift-info-room"
        response = client.post(url, json={"room_id": "22625025", "user_name": "test_user"})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert data["gifts"][0]["name"] == "小花花"
        assert data["gifts"][1]["coin_type"] == "silver"
