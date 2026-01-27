import pytest
from unittest.mock import patch, AsyncMock
from backend.app.services.user_service import user_service

@pytest.mark.asyncio
async def test_delete_user():
    # Mock the crud_dao used in user_service
    with patch("backend.app.services.user_service.crud_dao", new_callable=AsyncMock) as mock_crud:
        # Setup mock behavior
        mock_crud.delete_user_by_name.return_value = True
        
        # Call the service method
        result = await user_service.delete_user("test_user")
        
        # Assertions
        assert result is True
        # Verify that the crud method was called with the correct arguments
        # Note: The first argument to delete_user_by_name is 'db', which is a context manager result.
        # Since we are mocking crud_dao, we just check if it was called.
        # The db session is created inside the service method, so it's a bit hard to verify the exact db instance,
        # but we can verify the user_name.
        args, _ = mock_crud.delete_user_by_name.call_args
        assert args[1] == "test_user"

    with patch("backend.app.services.user_service.crud_dao", new_callable=AsyncMock) as mock_crud:
        # Test failure case
        mock_crud.delete_user_by_name.return_value = False
        result = await user_service.delete_user("unknown_user")
        assert result is False
