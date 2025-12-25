import pytest
from unittest.mock import Mock, AsyncMock
from cross_web import StarletteRequestAdapter


@pytest.mark.asyncio
async def test_starlette_adapter_headers_caching() -> None:
    """Test that headers are cached after first access"""
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.query_params = {}
    mock_request.headers = {"x-test": "value", "content-type": "text/plain"}
    mock_request.url = "http://example.com"
    mock_request.cookies = {}

    adapter = StarletteRequestAdapter(mock_request)

    # First access should cache headers
    headers1 = adapter.headers
    assert headers1["x-test"] == "value"

    # Second access should return cached headers
    headers2 = adapter.headers
    assert headers2 is headers1  # Same object reference

    # Content type should work via cached headers
    assert adapter.content_type == "text/plain"


@pytest.mark.asyncio
async def test_starlette_adapter_no_content_type() -> None:
    """Test when content-type header is missing"""
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.query_params = {}
    mock_request.headers = {"x-other": "value"}
    mock_request.url = "http://example.com"
    mock_request.cookies = {}

    adapter = StarletteRequestAdapter(mock_request)

    assert adapter.content_type is None


@pytest.mark.asyncio
async def test_starlette_adapter_empty_body() -> None:
    """Test get_body with empty body"""
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.query_params = {}
    mock_request.headers = {}
    mock_request.url = "http://example.com"
    mock_request.cookies = {}
    mock_request.body = AsyncMock(return_value=b"")

    adapter = StarletteRequestAdapter(mock_request)

    body = await adapter.get_body()
    assert body == b""


@pytest.mark.asyncio
async def test_starlette_adapter_form_only() -> None:
    """Test get_form_data with only form data (no files)"""
    mock_request = Mock()
    mock_request.method = "POST"
    mock_request.query_params = {}
    mock_request.headers = {"content-type": "application/x-www-form-urlencoded"}
    mock_request.url = "http://example.com"
    mock_request.cookies = {}

    # Mock form data without files
    mock_form_data = {"field1": "value1", "field2": "value2"}
    mock_request.form = AsyncMock(return_value=mock_form_data)

    adapter = StarletteRequestAdapter(mock_request)

    form_data = await adapter.get_form_data()
    assert form_data.form == mock_form_data
    assert (
        form_data.files == mock_form_data
    )  # In Starlette adapter, both point to same data
