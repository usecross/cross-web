from __future__ import annotations

import pytest

pytest.importorskip("django")

from django.core.exceptions import BadRequest
from django.http import Http404, HttpRequest, HttpResponse
from django.test.client import AsyncRequestFactory, RequestFactory

from cross_web.testing import _django_urls
from cross_web.testing.clients import django as django_client_module
from cross_web.testing.clients.django import AsyncDjangoHttpClient, DjangoHttpClient

pytestmark = [pytest.mark.django]


def test_django_test_urlconf_is_empty() -> None:
    assert _django_urls.urlpatterns == []


def test_sync_build_request_data_requires_mapping_for_files() -> None:
    client = DjangoHttpClient(lambda request: HttpResponse())

    with pytest.raises(TypeError, match="mapping form data"):
        client._build_request_data(
            b"payload",
            None,
            {"file": ("test.txt", b"body", None)},
            None,
        )


def test_sync_build_request_data_preserves_content_type_for_bytes() -> None:
    client = DjangoHttpClient(lambda request: HttpResponse())

    request_data, request_kwargs = client._build_request_data(
        b"payload",
        None,
        None,
        {"Content-Type": "application/octet-stream"},
    )

    assert request_data == b"payload"
    assert request_kwargs == {"content_type": "application/octet-stream"}


@pytest.mark.asyncio
async def test_sync_do_request_handles_http404() -> None:
    def view(request: HttpRequest) -> HttpResponse:
        raise Http404

    client = DjangoHttpClient(view)

    response = await client._do_request(RequestFactory().get("/"))

    assert response.status_code == 404
    assert response.data == b"Not found"


@pytest.mark.asyncio
async def test_sync_do_request_handles_bad_request() -> None:
    def view(request: HttpRequest) -> HttpResponse:
        raise BadRequest("bad request")

    client = DjangoHttpClient(view)

    response = await client._do_request(RequestFactory().get("/"))

    assert response.status_code == 400
    assert response.data == b"bad request"


def test_async_build_request_data_requires_mapping_for_files() -> None:
    async def view(request: HttpRequest) -> HttpResponse:
        return HttpResponse()

    client = AsyncDjangoHttpClient(view)

    with pytest.raises(TypeError, match="mapping form data"):
        client._build_request_data(
            b"payload",
            None,
            {"file": ("test.txt", b"body", None)},
            None,
        )


def test_async_build_request_data_preserves_content_type_for_bytes() -> None:
    async def view(request: HttpRequest) -> HttpResponse:
        return HttpResponse()

    client = AsyncDjangoHttpClient(view)

    request_data, request_kwargs = client._build_request_data(
        b"payload",
        None,
        None,
        {"Content-Type": "application/octet-stream"},
    )

    assert request_data == b"payload"
    assert request_kwargs == {"content_type": "application/octet-stream"}


@pytest.mark.asyncio
async def test_async_do_request_handles_http404() -> None:
    async def view(request: HttpRequest) -> HttpResponse:
        raise Http404

    client = AsyncDjangoHttpClient(view)

    response = await client._do_request(AsyncRequestFactory().get("/"))

    assert response.status_code == 404
    assert response.data == b"Not found"


@pytest.mark.asyncio
async def test_async_do_request_handles_bad_request() -> None:
    async def view(request: HttpRequest) -> HttpResponse:
        raise BadRequest("bad request")

    client = AsyncDjangoHttpClient(view)

    response = await client._do_request(AsyncRequestFactory().get("/"))

    assert response.status_code == 400
    assert response.data == b"bad request"


@pytest.mark.asyncio
async def test_async_do_request_handles_streaming_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeStreamingResponse:
        status_code = 200
        headers = {"Content-Type": "text/plain"}
        streaming_content = [b"stream", b"ing"]

        @property
        def content(self) -> bytes:
            return b""

    monkeypatch.setattr(
        django_client_module, "StreamingHttpResponse", FakeStreamingResponse
    )

    async def view(request: HttpRequest) -> FakeStreamingResponse:
        return FakeStreamingResponse()

    client = AsyncDjangoHttpClient(view)

    response = await client._do_request(AsyncRequestFactory().get("/"))

    assert response.status_code == 200
    assert response.data == b"streaming"
