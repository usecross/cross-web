import pytest

from cross_web import QuartHTTPRequestAdapter

pytestmark = [pytest.mark.quart]


@pytest.mark.asyncio
async def test_quart_adapter() -> None:
    from quart import Quart

    app = Quart(__name__)

    adapter_result = None

    @app.post("/test")  # type: ignore[misc]
    async def handler() -> dict[str, str]:
        from quart import request

        nonlocal adapter_result
        adapter_result = QuartHTTPRequestAdapter(request)
        return {"status": "ok"}

    async with app.test_client() as client:
        # Set cookies on client with proper arguments
        client.set_cookie("localhost", "session", "123")
        # Test with JSON data
        await client.post("/test?query=test", json={"key": "value"})

        assert adapter_result is not None
        assert adapter_result.query_params == {"query": "test"}
        body = await adapter_result.get_body()
        assert body == b'{"key": "value"}'
        assert adapter_result.method == "POST"
        assert adapter_result.headers["Content-Type"] == "application/json"
        assert adapter_result.content_type == "application/json"
        assert "test" in adapter_result.url
        assert dict(adapter_result.cookies) == {"session": "123"}


@pytest.mark.asyncio
async def test_quart_adapter_form_data() -> None:
    from quart import Quart
    from werkzeug.datastructures import FileStorage
    import io

    app = Quart(__name__)

    adapter_result = None

    @app.post("/test")  # type: ignore[misc]
    async def handler() -> dict[str, str]:
        from quart import request

        nonlocal adapter_result
        adapter_result = QuartHTTPRequestAdapter(request)
        return {"status": "ok"}

    async with app.test_client() as client:
        # Set cookies on client
        client.set_cookie("localhost", "session", "123")
        # Test with form data and files
        file_obj = FileStorage(
            stream=io.BytesIO(b"upload"), filename="test.txt", content_type="text/plain"
        )
        await client.post(
            "/test?query=test",
            form={"form": "data"},
            files={"file": file_obj},
        )

        assert adapter_result is not None
        assert adapter_result.query_params == {"query": "test"}
        assert adapter_result.method == "POST"
        assert adapter_result.headers["Content-Type"].startswith("multipart/form-data")
        assert (
            adapter_result.content_type is not None
            and adapter_result.content_type.startswith("multipart/form-data")
        )
        assert "test" in adapter_result.url
        assert dict(adapter_result.cookies) == {"session": "123"}

        form_data = await adapter_result.get_form_data()
        assert form_data.form["form"] == "data"
        assert "file" in form_data.files
