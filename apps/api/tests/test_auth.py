import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.api.deps import get_current_user


@pytest.mark.asyncio
async def test_dev_mode_returns_dev_user():
    """When clerk_jwks_url is empty, auth is bypassed."""
    with patch("app.api.deps.settings") as mock_settings:
        mock_settings.clerk_jwks_url = ""
        result = await get_current_user(credentials=None)
        assert result == "dev-user"


@pytest.mark.asyncio
async def test_missing_token_raises_401():
    """When clerk_jwks_url is set but no token provided, raises 401."""
    with patch("app.api.deps.settings") as mock_settings:
        mock_settings.clerk_jwks_url = "https://example.com/.well-known/jwks.json"
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=None)
        assert exc_info.value.status_code == 401
        assert "Missing authentication token" in exc_info.value.detail
