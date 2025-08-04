import pytest
from unittest.mock import AsyncMock, MagicMock

from lia import AiohttpHTTPRequestAdapter

pytestmark = [pytest.mark.aiohttp]


@pytest.mark.asyncio
async def test_aiohttp_adapter_json() -> None:
    from aiohttp import web
    from aiohttp.test_utils import TestClient, TestServer

    adapter_result = None

    async def handler(request: web.Request) -> web.Response:
        nonlocal adapter_result
        adapter_result = await AiohttpHTTPRequestAdapter.create(request)
        return web.json_response({"status": "ok"})

    app = web.Application()
    app.router.add_post("/test", handler)

    async with TestClient(TestServer(app)) as client:
        await client.post(
            "/test?query=test", json={"key": "value"}, cookies={"session": "123"}
        )

        assert adapter_result is not None
        assert adapter_result.query_params == {"query": "test"}
        assert adapter_result.method == "POST"
        assert adapter_result.headers["content-type"] == "application/json"
        assert adapter_result.content_type == "application/json"
        assert "test" in str(adapter_result.url)
        assert adapter_result.cookies == {"session": "123"}

        body = await adapter_result.get_body()
        assert body == b'{"key": "value"}'


@pytest.mark.asyncio
async def test_aiohttp_adapter_form_data() -> None:
    from aiohttp import web, FormData
    from aiohttp.test_utils import TestClient, TestServer

    adapter_result = None

    async def handler(request: web.Request) -> web.Response:
        nonlocal adapter_result
        adapter_result = await AiohttpHTTPRequestAdapter.create(request)
        return web.json_response({"status": "ok"})

    app = web.Application()
    app.router.add_post("/test", handler)

    async with TestClient(TestServer(app)) as client:
        # Create form data with file
        data = FormData()
        data.add_field("form", "data")
        data.add_field(
            "file", b"upload", filename="test.txt", content_type="text/plain"
        )

        await client.post("/test?query=test", data=data, cookies={"session": "123"})

        assert adapter_result is not None
        assert adapter_result.query_params == {"query": "test"}
        assert adapter_result.method == "POST"
        content_type = adapter_result.headers.get("content-type")
        assert content_type is not None
        assert content_type.startswith("multipart/form-data")
        assert adapter_result.content_type is not None
        assert adapter_result.content_type.startswith("multipart/form-data")
        assert "test" in str(adapter_result.url)
        assert adapter_result.cookies == {"session": "123"}

        form_data = await adapter_result.get_form_data()
        assert form_data.form["form"] == "data"
        assert "file" in form_data.files


@pytest.mark.asyncio
async def test_aiohttp_adapter_get_body_none() -> None:
    """Test get_body() when _body is None (line 60)"""
    # Create a mock request
    mock_request = AsyncMock()
    mock_request.read = AsyncMock(return_value=b"test body")

    # Create adapter directly without pre-reading body
    adapter = AiohttpHTTPRequestAdapter(mock_request, body=None)

    # Call get_body() - this should trigger the read
    body = await adapter.get_body()
    assert body == b"test body"
    mock_request.read.assert_called_once()


@pytest.mark.asyncio
async def test_aiohttp_adapter_multipart_runtime_error() -> None:
    """Test get_form_data() with multipart raises RuntimeError (lines 75-77)"""
    # Create a mock request with multipart content type
    mock_request = MagicMock()
    mock_request.headers = {"content-type": "multipart/form-data; boundary=----"}

    # Create adapter directly without pre-processing multipart
    adapter = AiohttpHTTPRequestAdapter(mock_request, form_data=None)

    # Should raise RuntimeError
    with pytest.raises(RuntimeError, match="Multipart data should be pre-processed"):
        await adapter.get_form_data()


@pytest.mark.asyncio
async def test_aiohttp_adapter_urlencoded_form() -> None:
    """Test get_form_data() with URL-encoded form data (lines 79-81)"""
    # Create a mock request with URL-encoded form data
    mock_request = AsyncMock()
    mock_request.headers = {"content-type": "application/x-www-form-urlencoded"}
    mock_request.post = AsyncMock(return_value={"field1": "value1", "field2": "value2"})

    # Create adapter directly without pre-processing form data
    adapter = AiohttpHTTPRequestAdapter(mock_request, form_data=None)

    # Call get_form_data() - this should parse URL-encoded data
    form_data = await adapter.get_form_data()
    assert form_data.form == {"field1": "value1", "field2": "value2"}
    assert form_data.files == {}
    mock_request.post.assert_called_once()
