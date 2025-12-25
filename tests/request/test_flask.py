import io
import json
import pytest

from cross_web import AsyncFlaskHTTPRequestAdapter, FlaskHTTPRequestAdapter

pytestmark = [pytest.mark.flask]


def test_sync_flask_adapter() -> None:
    from flask import Flask

    app = Flask(__name__)

    # Create test context directly
    with app.test_request_context(
        "/test?query=test",
        method="POST",
        data={"form": "data", "file": (io.BytesIO(b"upload"), "test.txt")},
        headers={"Cookie": "session=123"},
    ):
        from flask import request

        adapter = FlaskHTTPRequestAdapter(request)

        assert adapter.query_params == {"query": "test"}
        assert adapter.method == "POST"
        assert adapter.headers["Content-Type"].startswith("multipart/form-data")
        assert adapter.post_data["form"] == "data"
        assert "file" in adapter.files
        assert adapter.content_type is not None and adapter.content_type.startswith(
            "multipart/form-data"
        )
        assert "/test" in adapter.url
        assert dict(adapter.cookies) == {"session": "123"}

        form_data = adapter.get_form_data()
        assert "file" in form_data.files
        assert form_data.form["form"] == "data"


def test_sync_flask_adapter_json() -> None:
    from flask import Flask

    app = Flask(__name__)

    with app.test_request_context(
        "/test?query=test",
        method="POST",
        data=json.dumps({"key": "value"}),
        content_type="application/json",
        headers={"Cookie": "session=123"},
    ):
        from flask import request

        adapter = FlaskHTTPRequestAdapter(request)

        assert adapter.query_params == {"query": "test"}
        assert adapter.body == '{"key": "value"}'
        assert adapter.method == "POST"
        assert adapter.headers["Content-Type"] == "application/json"
        assert adapter.content_type == "application/json"
        assert "/test" in adapter.url
        assert dict(adapter.cookies) == {"session": "123"}


@pytest.mark.asyncio
async def test_async_flask_adapter() -> None:
    from flask import Flask

    app = Flask(__name__)

    with app.test_request_context(
        "/test?query=test",
        method="POST",
        data=json.dumps({"key": "value"}),
        content_type="application/json",
        headers={"Cookie": "session=123"},
    ):
        from flask import request

        adapter = AsyncFlaskHTTPRequestAdapter(request)

        assert adapter.query_params == {"query": "test"}
        body = await adapter.get_body()
        assert body == b'{"key": "value"}'
        assert adapter.method == "POST"
        assert adapter.headers["Content-Type"] == "application/json"
        assert adapter.content_type == "application/json"
        assert "/test" in adapter.url
        assert dict(adapter.cookies) == {"session": "123"}


@pytest.mark.asyncio
async def test_async_flask_adapter_multipart() -> None:
    from flask import Flask

    app = Flask(__name__)

    # Create test context with multipart data
    with app.test_request_context(
        "/test?query=test",
        method="POST",
        data={"form": "data", "file": (io.BytesIO(b"upload"), "test.txt")},
        headers={"Cookie": "session=123"},
    ):
        from flask import request

        adapter = AsyncFlaskHTTPRequestAdapter(request)

        assert adapter.query_params == {"query": "test"}
        assert adapter.method == "POST"
        assert adapter.headers["Content-Type"].startswith("multipart/form-data")
        assert adapter.content_type is not None and adapter.content_type.startswith(
            "multipart/form-data"
        )
        assert "/test" in adapter.url
        assert dict(adapter.cookies) == {"session": "123"}

        form_data = await adapter.get_form_data()
        assert "file" in form_data.files
        assert form_data.form["form"] == "data"
