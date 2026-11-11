from collections.abc import Mapping
from typing import Optional, Union

from cross_web.request._base import (
    AsyncHTTPRequestAdapter,
    FormData,
    HTTPMethod,
    PathParams,
    QueryParams,
    SyncHTTPRequestAdapter,
)


def test_form_data_creation() -> None:
    files = {"file1": "content1"}
    form = {"field1": "value1", "field2": "value2"}

    form_data = FormData(files=files, form=form)

    assert form_data.files == files
    assert form_data.form == form


def test_form_data_get_existing_key() -> None:
    form_data = FormData(
        files={"upload": "data"}, form={"username": "john", "email": "john@example.com"}
    )

    assert form_data.get("username") == "john"
    assert form_data.get("email") == "john@example.com"


def test_form_data_get_missing_key() -> None:
    form_data = FormData(files={}, form={"name": "test"})

    assert form_data.get("missing") is None


def test_form_data_get_from_files() -> None:
    # The get method only retrieves from form, not files
    form_data = FormData(
        files={"file_key": "file_value"}, form={"form_key": "form_value"}
    )

    assert form_data.get("form_key") == "form_value"
    assert form_data.get("file_key") is None  # Files are not accessed via get()


def test_form_data_empty() -> None:
    form_data = FormData(files={}, form={})

    assert form_data.files == {}
    assert form_data.form == {}
    assert form_data.get("anything") is None


class _OlderSyncAdapter(SyncHTTPRequestAdapter):
    """An adapter written before ``client_host`` existed."""

    method: HTTPMethod = "GET"
    query_params: QueryParams = {}
    path_params: PathParams = {}
    headers: Mapping[str, str] = {}
    content_type: Optional[str] = None
    body: Union[str, bytes] = b""
    post_data: Mapping[str, Union[str, bytes]] = {}
    files: Mapping[str, object] = {}
    url = "http://testserver/"
    cookies: Mapping[str, str] = {}

    def get_form_data(self) -> FormData:
        return FormData(files={}, form={})


class _OlderAsyncAdapter(AsyncHTTPRequestAdapter):
    """An adapter written before ``client_host`` existed."""

    method: HTTPMethod = "GET"
    query_params: QueryParams = {}
    path_params: PathParams = {}
    headers: Mapping[str, str] = {}
    content_type: Optional[str] = None
    url = "http://testserver/"
    cookies: Mapping[str, str] = {}

    async def get_body(self) -> bytes:
        return b""

    async def get_form_data(self) -> FormData:
        return FormData(files={}, form={})


def test_adapters_without_client_host_report_none() -> None:
    assert _OlderSyncAdapter().client_host is None
    assert _OlderAsyncAdapter().client_host is None
