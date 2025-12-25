import pytest

from cross_web import LitestarRequestAdapter

pytestmark = [pytest.mark.litestar]


@pytest.mark.asyncio
async def test_litestar_adapter() -> None:
    from litestar import Litestar, post, Request
    from litestar.testing import TestClient

    adapter_result = None

    @post("/test")  # type: ignore[misc]
    async def handler(request: Request) -> dict[str, str]:
        nonlocal adapter_result
        adapter_result = LitestarRequestAdapter(request)
        return {"status": "ok"}

    app = Litestar([handler])

    with TestClient(app=app) as client:
        client.cookies["session"] = "123"
        client.post("/test?query=test", json={"key": "value"})

        assert adapter_result is not None
        assert dict(adapter_result.query_params) == {"query": "test"}
        assert adapter_result.method == "POST"
        assert adapter_result.headers["content-type"] == "application/json"
        assert adapter_result.content_type == "application/json"
        assert "test" in adapter_result.url
        assert dict(adapter_result.cookies) == {"session": "123"}


@pytest.mark.asyncio
async def test_litestar_adapter_form_data() -> None:
    from litestar import Litestar, post, Request
    from litestar.testing import TestClient

    adapter_result = None

    @post("/test")  # type: ignore[misc]
    async def handler(request: Request) -> dict[str, str]:
        nonlocal adapter_result
        adapter_result = LitestarRequestAdapter(request)
        return {"status": "ok"}

    app = Litestar([handler])

    with TestClient(app=app) as client:
        client.cookies["session"] = "123"
        client.post(
            "/test?query=test",
            data={"form": "data"},
            files={"file": ("test.txt", b"upload")},
        )

        assert adapter_result is not None
        assert dict(adapter_result.query_params) == {"query": "test"}
        assert adapter_result.method == "POST"
        assert adapter_result.headers[
            "content-type"
        ] is not None and adapter_result.headers["content-type"].startswith(
            "multipart/form-data"
        )
        assert (
            adapter_result.content_type is not None
            and adapter_result.content_type.startswith("multipart/form-data")
        )
        assert "test" in adapter_result.url
        assert dict(adapter_result.cookies) == {"session": "123"}
