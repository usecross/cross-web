import pytest
from cross_web.request._testing import TestingRequestAdapter
from cross_web.request._base import FormData


@pytest.mark.asyncio
async def test_testing_request_adapter_defaults() -> None:
    adapter = TestingRequestAdapter()

    assert adapter.method == "POST"
    assert adapter.query_params == {}
    assert adapter.headers == {}
    assert adapter.content_type is None
    assert adapter.url == "http://testserver/"
    assert adapter.cookies == {}

    body = await adapter.get_body()
    assert body == b""

    form_data = await adapter.get_form_data()
    assert form_data.files == {}
    assert form_data.form == {}


@pytest.mark.asyncio
async def test_testing_request_adapter_custom_values() -> None:
    adapter = TestingRequestAdapter(
        method="GET",
        query_params={"key": "value"},
        headers={"X-Custom": "header"},
        content_type="application/json",
        url="http://example.com/test",
        cookies={"session": "abc123"},
        form_data=FormData(files={"file": "data"}, form={"field": "value"}),
    )

    assert adapter.method == "GET"
    assert adapter.query_params == {"key": "value"}
    assert adapter.headers == {"X-Custom": "header"}
    assert adapter.content_type == "application/json"
    assert adapter.url == "http://example.com/test"
    assert adapter.cookies == {"session": "abc123"}

    form_data = await adapter.get_form_data()
    assert form_data.files == {"file": "data"}
    assert form_data.form == {"field": "value"}


@pytest.mark.asyncio
async def test_testing_request_adapter_json_body() -> None:
    json_data = {"test": "data", "number": 123}
    adapter = TestingRequestAdapter(json=json_data)

    body = await adapter.get_body()
    assert body == b'{"test": "data", "number": 123}'


@pytest.mark.asyncio
async def test_testing_request_adapter_mixed_data() -> None:
    # Test that json takes precedence over form_data for body
    adapter = TestingRequestAdapter(
        json={"json": "data"},
        form_data=FormData(files={}, form={"form": "data"}),
    )

    body = await adapter.get_body()
    assert body == b'{"json": "data"}'

    # But form_data is still accessible via get_form_data
    form_data = await adapter.get_form_data()
    assert form_data.form == {"form": "data"}


@pytest.mark.asyncio
async def test_testing_request_adapter_empty_json() -> None:
    adapter = TestingRequestAdapter(json={})

    body = await adapter.get_body()
    assert body == b"{}"


@pytest.mark.asyncio
async def test_testing_request_adapter_complex_json() -> None:
    complex_data = {
        "nested": {"inner": [1, 2, 3]},
        "boolean": True,
        "null": None,
        "string": "test",
    }
    adapter = TestingRequestAdapter(json=complex_data)

    body = await adapter.get_body()
    import json

    decoded = json.loads(body)
    assert decoded == complex_data
