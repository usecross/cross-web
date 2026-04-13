from typing import Any, Optional, cast

import pytest

from cross_web.testing import HttpClient


@pytest.mark.asyncio
async def test_request_adapter_json(http_client: HttpClient) -> None:
    response = await http_client.post(
        "/request/abc?query=test",
        json={"key": "value"},
        cookies={"session": "123"},
    )
    result = cast(dict[str, Any], response.json)

    assert response.status_code == 200
    assert result["query_params"] == {"query": "test"}
    assert result["path_params"] == {"item_id": "abc"}
    assert result["method"] == "POST"
    assert result["header_content_type"] == "application/json"
    assert result["content_type"] == "application/json"
    assert result["url_path"] == "/request/abc"
    assert result["url_query"] == "query=test"
    assert result["cookies"] == {"session": "123"}
    assert result["body_json"] == {"key": "value"}


@pytest.mark.asyncio
async def test_request_adapter_form_data(http_client: HttpClient) -> None:
    if not http_client.supports_form_data:
        pytest.skip("This framework adapter does not support form data")

    response = await http_client.post(
        "/request/abc?query=test",
        data={"form": "data"},
        files={"file": ("test.txt", b"upload", "text/plain")},
        cookies={"session": "123"},
    )
    result = cast(dict[str, Any], response.json)

    assert response.status_code == 200
    header_content_type = cast(Optional[str], result["header_content_type"])
    content_type = cast(Optional[str], result["content_type"])

    assert result["query_params"] == {"query": "test"}
    assert result["path_params"] == {"item_id": "abc"}
    assert result["method"] == "POST"
    assert header_content_type is not None
    assert header_content_type.startswith("multipart/form-data")
    assert content_type is not None
    assert content_type.startswith("multipart/form-data")
    assert result["url_path"] == "/request/abc"
    assert result["url_query"] == "query=test"
    assert result["cookies"] == {"session": "123"}
    assert result["form_value"] == "data"
    assert result["has_file"] is True

    if "post_form_value" in result:
        assert result["post_form_value"] == "data"

    if "files_has_file" in result:
        assert result["files_has_file"] is True
