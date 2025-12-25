import pytest
from cross_web.request import AsyncHTTPRequest
from cross_web.request._base import FormData
from cross_web.request._testing import TestingRequestAdapter


def test_async_http_request_init() -> None:
    adapter = TestingRequestAdapter()
    request = AsyncHTTPRequest(adapter)
    assert request._adapter is adapter


@pytest.mark.asyncio
async def test_async_http_request_properties() -> None:
    adapter = TestingRequestAdapter(
        method="PUT",
        query_params={"q": "search"},
        headers={"Authorization": "Bearer token"},
        content_type="application/json",
        url="https://api.example.com/endpoint",
        cookies={"session_id": "xyz789"},
    )
    request = AsyncHTTPRequest(adapter)

    assert request.method == "PUT"
    assert request.query_params == {"q": "search"}
    assert request.headers == {"Authorization": "Bearer token"}
    assert request.content_type == "application/json"
    assert request.url == "https://api.example.com/endpoint"
    assert request.cookies == {"session_id": "xyz789"}


@pytest.mark.asyncio
async def test_async_http_request_get_body() -> None:
    adapter = TestingRequestAdapter(json={"data": "test"})
    request = AsyncHTTPRequest(adapter)

    body = await request.get_body()
    assert body == b'{"data": "test"}'


@pytest.mark.asyncio
async def test_async_http_request_get_form_data() -> None:
    form_data = FormData(
        files={"upload": "file_content"}, form={"name": "test", "value": "123"}
    )
    adapter = TestingRequestAdapter(form_data=form_data)
    request = AsyncHTTPRequest(adapter)

    result = await request.get_form_data()
    assert result.files == {"upload": "file_content"}
    assert result.form == {"name": "test", "value": "123"}


@pytest.mark.asyncio
async def test_from_form_data() -> None:
    data = {"username": "john", "password": "secret"}
    request = AsyncHTTPRequest.from_form_data(data)

    assert request.method == "POST"
    assert request.content_type == "application/x-www-form-urlencoded"

    # Check form data was set correctly
    form_data = await request.get_form_data()
    assert form_data.form == data
    assert form_data.files == {}


@pytest.mark.asyncio
async def test_from_form_data_get_form_data() -> None:
    data = {"field1": "value1", "field2": "value2"}
    request = AsyncHTTPRequest.from_form_data(data)

    form_data = await request.get_form_data()
    assert form_data.form == data
    assert form_data.files == {}


# Test framework-specific constructors
def test_from_starlette() -> None:
    """Test creating AsyncHTTPRequest from Starlette request."""
    from unittest.mock import Mock

    # Mock a Starlette request
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.url.path = "/test"
    mock_request.query_params = {}
    mock_request.headers = {}

    # Create AsyncHTTPRequest from Starlette
    request = AsyncHTTPRequest.from_starlette(mock_request)

    # Verify it's an AsyncHTTPRequest instance
    assert isinstance(request, AsyncHTTPRequest)
    # Verify the adapter was created correctly
    assert request._adapter.__class__.__name__ == "StarletteRequestAdapter"


def test_from_fastapi() -> None:
    """Test creating AsyncHTTPRequest from FastAPI request (uses Starlette)."""
    from unittest.mock import Mock

    # Mock a FastAPI/Starlette request
    mock_request = Mock()
    mock_request.method = "POST"
    mock_request.url.path = "/api"
    mock_request.query_params = {}
    mock_request.headers = {}

    # Create AsyncHTTPRequest from FastAPI
    request = AsyncHTTPRequest.from_fastapi(mock_request)

    # Verify it's an AsyncHTTPRequest instance
    assert isinstance(request, AsyncHTTPRequest)
    # FastAPI uses Starlette adapter
    assert request._adapter.__class__.__name__ == "StarletteRequestAdapter"


def test_from_django() -> None:
    """Test creating AsyncHTTPRequest from Django request."""
    from unittest.mock import Mock

    # Mock a Django request
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.GET = {}
    mock_request.META = {}
    mock_request.body = b""

    # Create AsyncHTTPRequest from Django
    request = AsyncHTTPRequest.from_django(mock_request)

    # Verify it's an AsyncHTTPRequest instance
    assert isinstance(request, AsyncHTTPRequest)
    # Verify the adapter was created correctly
    assert request._adapter.__class__.__name__ == "AsyncDjangoHTTPRequestAdapter"


def test_from_flask() -> None:
    """Test creating AsyncHTTPRequest from Flask request."""
    from unittest.mock import Mock

    # Mock a Flask request
    mock_request = Mock()
    mock_request.method = "POST"
    mock_request.args = {}
    mock_request.headers = {}
    mock_request.get_data = Mock(return_value=b"test")

    # Create AsyncHTTPRequest from Flask
    request = AsyncHTTPRequest.from_flask(mock_request)

    # Verify it's an AsyncHTTPRequest instance
    assert isinstance(request, AsyncHTTPRequest)
    # Verify the adapter was created correctly
    assert request._adapter.__class__.__name__ == "AsyncFlaskHTTPRequestAdapter"


def test_from_sanic() -> None:
    """Test creating AsyncHTTPRequest from Sanic request."""
    from unittest.mock import Mock

    # Mock a Sanic request
    mock_request = Mock()
    mock_request.method = "PUT"
    mock_request.args = {}
    mock_request.headers = {}
    mock_request.body = b""

    # Create AsyncHTTPRequest from Sanic
    request = AsyncHTTPRequest.from_sanic(mock_request)

    # Verify it's an AsyncHTTPRequest instance
    assert isinstance(request, AsyncHTTPRequest)
    # Verify the adapter was created correctly
    assert request._adapter.__class__.__name__ == "SanicHTTPRequestAdapter"


def test_from_aiohttp() -> None:
    """Test creating AsyncHTTPRequest from aiohttp request."""
    from unittest.mock import Mock

    # Mock an aiohttp request
    mock_request = Mock()
    mock_request.method = "DELETE"
    mock_request.query = {}
    mock_request.headers = {}

    # Create AsyncHTTPRequest from aiohttp
    request = AsyncHTTPRequest.from_aiohttp(mock_request)

    # Verify it's an AsyncHTTPRequest instance
    assert isinstance(request, AsyncHTTPRequest)
    # Verify the adapter was created correctly
    assert request._adapter.__class__.__name__ == "AiohttpHTTPRequestAdapter"


def test_from_quart() -> None:
    """Test creating AsyncHTTPRequest from Quart request."""
    from unittest.mock import Mock

    # Mock a Quart request
    mock_request = Mock()
    mock_request.method = "PATCH"
    mock_request.args = {}
    mock_request.headers = {}

    # Create AsyncHTTPRequest from Quart
    request = AsyncHTTPRequest.from_quart(mock_request)

    # Verify it's an AsyncHTTPRequest instance
    assert isinstance(request, AsyncHTTPRequest)
    # Verify the adapter was created correctly
    assert request._adapter.__class__.__name__ == "QuartHTTPRequestAdapter"


def test_from_litestar() -> None:
    """Test creating AsyncHTTPRequest from Litestar request."""
    from unittest.mock import Mock

    # Mock a Litestar request
    mock_request = Mock()
    mock_request.method = "HEAD"
    mock_request.query_params = {}
    mock_request.headers = {}

    # Create AsyncHTTPRequest from Litestar
    request = AsyncHTTPRequest.from_litestar(mock_request)

    # Verify it's an AsyncHTTPRequest instance
    assert isinstance(request, AsyncHTTPRequest)
    # Verify the adapter was created correctly
    assert request._adapter.__class__.__name__ == "LitestarRequestAdapter"
