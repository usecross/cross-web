import pytest

from lia import LitestarRequestAdapter

pytestmark = [pytest.mark.litestar]


@pytest.mark.asyncio
async def test_litestar_adapter():
    from litestar import Litestar, post, Request
    from litestar.testing import TestClient

    adapter_result = None

    @post("/test")
    async def handler(request: Request) -> dict:
        nonlocal adapter_result
        adapter_result = LitestarRequestAdapter(request)
        return {"status": "ok"}

    app = Litestar([handler])

    with TestClient(app=app) as client:
        response = client.post(
            "/test?query=test", json={"key": "value"}, cookies={"session": "123"}
        )

        assert adapter_result is not None
        assert dict(adapter_result.query_params) == {"query": "test"}
        assert adapter_result.method == "POST"
        assert adapter_result.headers["content-type"] == "application/json"
        assert adapter_result.content_type == "application/json"
        assert "test" in adapter_result.url
        assert dict(adapter_result.cookies) == {"session": "123"}


@pytest.mark.asyncio
async def test_litestar_adapter_form_data():
    from litestar import Litestar, post, Request
    from litestar.testing import TestClient
    import io

    adapter_result = None

    @post("/test")
    async def handler(request: Request) -> dict:
        nonlocal adapter_result
        adapter_result = LitestarRequestAdapter(request)
        return {"status": "ok"}

    app = Litestar([handler])

    with TestClient(app=app) as client:
        response = client.post(
            "/test?query=test",
            data={"form": "data"},
            files={"file": ("test.txt", b"upload")},
            cookies={"session": "123"},
        )

        assert adapter_result is not None
        assert dict(adapter_result.query_params) == {"query": "test"}
        assert adapter_result.method == "POST"
        assert adapter_result.headers["content-type"].startswith("multipart/form-data")
        assert adapter_result.content_type.startswith("multipart/form-data")
        assert "test" in adapter_result.url
        assert dict(adapter_result.cookies) == {"session": "123"}
