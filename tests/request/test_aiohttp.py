import pytest

from lia import AiohttpHTTPRequestAdapter

pytestmark = [pytest.mark.aiohttp]


@pytest.mark.asyncio
async def test_aiohttp_adapter_json():
    from aiohttp import web
    from aiohttp.test_utils import TestClient, TestServer

    adapter_result = None

    async def handler(request):
        nonlocal adapter_result
        adapter_result = await AiohttpHTTPRequestAdapter.create(request)
        return web.json_response({"status": "ok"})

    app = web.Application()
    app.router.add_post("/test", handler)

    async with TestClient(TestServer(app)) as client:
        response = await client.post(
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
async def test_aiohttp_adapter_form_data():
    from aiohttp import web, FormData
    from aiohttp.test_utils import TestClient, TestServer

    adapter_result = None

    async def handler(request):
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

        response = await client.post(
            "/test?query=test", data=data, cookies={"session": "123"}
        )

        assert adapter_result is not None
        assert adapter_result.query_params == {"query": "test"}
        assert adapter_result.method == "POST"
        assert adapter_result.headers["content-type"].startswith("multipart/form-data")
        assert adapter_result.content_type.startswith("multipart/form-data")
        assert "test" in str(adapter_result.url)
        assert adapter_result.cookies == {"session": "123"}

        form_data = await adapter_result.get_form_data()
        assert form_data.form["form"] == "data"
        assert "file" in form_data.files
