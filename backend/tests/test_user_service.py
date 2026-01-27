import pytest
from unittest.mock import patch, AsyncMock
from backend.app.services.user_service import user_service

@pytest.mark.asyncio
async def test_delete_user():
    # Mock the crud_dao used in user_service
    with patch("backend.app.services.user_service.crud_user", new_callable=AsyncMock) as mock_crud:
        # Mock the database session
        mock_db = AsyncMock()
        with patch("backend.app.services.user_service.AsyncSessionLocal", return_value=mock_db):
            # Setup mock behavior
            mock_crud.delete_user_by_name.return_value = True
            
            # Call the service method
            result = await user_service.delete_user("test_user")
            
            # Assertions
            assert result is True
            # Verify that the crud method was called with the correct arguments
            args, _ = mock_crud.delete_user_by_name.call_args
            assert args[1] == "test_user"
            
            # Verify commit was called
            mock_db.__aenter__.return_value.commit.assert_called_once()

    with patch("backend.app.services.user_service.crud_user", new_callable=AsyncMock) as mock_crud:
         # Mock the database session
        mock_db = AsyncMock()
        with patch("backend.app.services.user_service.AsyncSessionLocal", return_value=mock_db):
            # Test failure case
            mock_crud.delete_user_by_name.return_value = False
            result = await user_service.delete_user("unknown_user")
            assert result is False
            args, _ = mock_crud.delete_user_by_name.call_args
            assert args[1] == "unknown_user"
            
            # Verify commit was NOT called for failure
            mock_db.__aenter__.return_value.commit.assert_not_called()
