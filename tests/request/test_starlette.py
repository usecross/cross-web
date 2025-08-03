import pytest

from lia import StarletteRequestAdapter

pytestmark = [pytest.mark.starlette]


@pytest.mark.asyncio
async def test_starlette_adapter():
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route
    from starlette.testclient import TestClient

    adapter_result = None

    async def handler(request):
        nonlocal adapter_result
        adapter_result = StarletteRequestAdapter(request)
        return JSONResponse({"status": "ok"})

    app = Starlette(routes=[Route("/test", handler, methods=["POST"])])

    with TestClient(app) as client:
        response = client.post(
            "/test?query=test", json={"key": "value"}, cookies={"session": "123"}
        )

        assert adapter_result is not None
        assert dict(adapter_result.query_params) == {"query": "test"}
        assert adapter_result.method == "POST"
        assert adapter_result.headers["content-type"] == "application/json"
        assert adapter_result.content_type == "application/json"
        assert "test" in str(adapter_result.url)
        assert dict(adapter_result.cookies) == {"session": "123"}


@pytest.mark.asyncio
async def test_starlette_adapter_form_data():
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route
    from starlette.testclient import TestClient
    import io

    adapter_result = None

    async def handler(request):
        nonlocal adapter_result
        adapter_result = StarletteRequestAdapter(request)
        return JSONResponse({"status": "ok"})

    app = Starlette(routes=[Route("/test", handler, methods=["POST"])])

    with TestClient(app) as client:
        client.post(
            "/test?query=test",
            data={"form": "data"},
            files={"file": ("test.txt", io.BytesIO(b"upload"), "text/plain")},
            cookies={"session": "123"},
        )

        assert adapter_result is not None
        assert dict(adapter_result.query_params) == {"query": "test"}
        assert adapter_result.method == "POST"
        assert adapter_result.headers["content-type"].startswith("multipart/form-data")
        assert adapter_result.content_type.startswith("multipart/form-data")
        assert "test" in str(adapter_result.url)
        assert dict(adapter_result.cookies) == {"session": "123"}
