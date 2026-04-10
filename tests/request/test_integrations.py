import pytest

from .clients.base import RequestClient


@pytest.mark.asyncio
async def test_request_adapter_json(request_client: RequestClient) -> None:
    result = await request_client.json_request()

    assert result.query_params == {"query": "test"}
    assert result.method == "POST"
    assert result.header_content_type == "application/json"
    assert result.content_type == "application/json"
    assert result.url_path.endswith("/abc")
    assert result.url_query == "query=test"
    assert result.cookies == {"session": "123"}
    assert result.body_json == {"key": "value"}


@pytest.mark.asyncio
async def test_request_adapter_form_data(request_client: RequestClient) -> None:
    if not request_client.supports_form_data:
        pytest.skip("This framework adapter does not support form data")

    result = await request_client.form_request()

    assert result.query_params == {"query": "test"}
    assert result.method == "POST"
    assert result.header_content_type is not None
    assert result.header_content_type.startswith("multipart/form-data")
    assert result.content_type is not None
    assert result.content_type.startswith("multipart/form-data")
    assert result.url_path.endswith("/abc")
    assert result.url_query == "query=test"
    assert result.cookies == {"session": "123"}
    assert result.form_value == "data"
    assert result.has_file is True

    if result.post_form_value is not None:
        assert result.post_form_value == "data"

    if result.files_has_file is not None:
        assert result.files_has_file is True
