import pytest
from unittest.mock import Mock, patch
from cross_web.response import Cookie, Response


@pytest.mark.asyncio
async def test_to_fastapi_with_all_cookie_params() -> None:
    """Test to_fastapi with cookies having all parameters set"""
    cookies = [
        Cookie(
            name="session",
            value="abc123",
            secure=True,
            path="/api",
            domain="example.com",
            max_age=3600,
            httponly=True,
            samesite="strict",
        ),
        Cookie(
            name="prefs",
            value="dark_mode",
            secure=False,
            path=None,
            domain=None,
            max_age=None,
            httponly=False,
            samesite="lax",
        ),
    ]

    response = Response(
        status_code=200, body="Success", headers={"X-Custom": "Header"}, cookies=cookies
    )

    # Mock FastAPI Response
    with patch("fastapi.Response") as MockFastAPIResponse:
        mock_fastapi_response = Mock()
        MockFastAPIResponse.return_value = mock_fastapi_response

        result = response.to_fastapi()

        # Verify FastAPI Response was created with correct params
        MockFastAPIResponse.assert_called_once_with(
            status_code=200, headers={"X-Custom": "Header"}, content="Success"
        )

        # Verify set_cookie was called for each cookie with all params
        assert mock_fastapi_response.set_cookie.call_count == 2

        # First cookie call
        mock_fastapi_response.set_cookie.assert_any_call(
            "session",
            "abc123",
            secure=True,
            path="/api",
            domain="example.com",
            max_age=3600,
            httponly=True,
            samesite="strict",
        )

        # Second cookie call
        mock_fastapi_response.set_cookie.assert_any_call(
            "prefs",
            "dark_mode",
            secure=False,
            path=None,
            domain=None,
            max_age=None,
            httponly=False,
            samesite="lax",
        )

        assert result is mock_fastapi_response


@pytest.mark.asyncio
async def test_to_fastapi_no_cookies() -> None:
    """Test to_fastapi when cookies is None"""
    response = Response(
        status_code=404,
        body="Not Found",
        headers={"Content-Type": "text/plain"},
        cookies=None,
    )

    with patch("fastapi.Response") as MockFastAPIResponse:
        mock_fastapi_response = Mock()
        MockFastAPIResponse.return_value = mock_fastapi_response

        result = response.to_fastapi()

        # Verify FastAPI Response was created
        MockFastAPIResponse.assert_called_once_with(
            status_code=404, headers={"Content-Type": "text/plain"}, content="Not Found"
        )

        # Verify set_cookie was never called
        mock_fastapi_response.set_cookie.assert_not_called()

        assert result is mock_fastapi_response


@pytest.mark.asyncio
async def test_to_fastapi_empty_cookies_list() -> None:
    """Test to_fastapi when cookies is empty list"""
    response = Response(status_code=204, body=None, headers=None, cookies=[])

    with patch("fastapi.Response") as MockFastAPIResponse:
        mock_fastapi_response = Mock()
        MockFastAPIResponse.return_value = mock_fastapi_response

        result = response.to_fastapi()

        # Verify FastAPI Response was created
        MockFastAPIResponse.assert_called_once_with(
            status_code=204, headers=None, content=None
        )

        # Verify set_cookie was never called
        mock_fastapi_response.set_cookie.assert_not_called()

        assert result is mock_fastapi_response
