from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterable, Mapping
from json import dumps
from typing import Any

from django.core.exceptions import BadRequest, SuspiciousOperation
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404, HttpRequest, HttpResponse, StreamingHttpResponse
from django.test.client import AsyncRequestFactory, RequestFactory

from .base import HttpClient, RequestData, Response, UploadedFile, merge_cookies


def ensure_django_setup() -> None:
    import django
    from django.conf import settings

    if settings.configured:
        return

    settings.configure(
        DEBUG=True,
        SECRET_KEY="test-secret-key",
        DEFAULT_CHARSET="utf-8",
        USE_TZ=True,
        ALLOWED_HOSTS=["*"],
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
        ],
        MIDDLEWARE=[],
        ROOT_URLCONF=__name__,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
    )
    django.setup()


class DjangoHttpClient(HttpClient):
    def __init__(self, view: Callable[[HttpRequest], HttpResponse]) -> None:
        ensure_django_setup()
        self.view = view

    def _to_django_headers(self, headers: Mapping[str, str]) -> dict[str, str]:
        return {
            f"HTTP_{key.upper().replace('-', '_')}": value
            for key, value in headers.items()
        }

    def _build_request_data(
        self,
        data: RequestData | None,
        json_data: object | None,
        files: dict[str, UploadedFile] | None,
        headers: dict[str, str] | None,
    ) -> tuple[object | None, dict[str, Any]]:
        request_kwargs: dict[str, Any] = {}
        request_data: object | None = data

        if json_data is not None:
            request_data = dumps(json_data)
            request_kwargs["content_type"] = "application/json"

        if files:
            if request_data is not None and not isinstance(request_data, Mapping):
                raise TypeError("Django multipart requests require mapping form data")

            multipart_data = dict(request_data or {})
            for key, (filename, content, content_type) in files.items():
                multipart_data[key] = SimpleUploadedFile(
                    filename,
                    content,
                    content_type=content_type or "application/octet-stream",
                )
            request_data = multipart_data
        elif (
            request_data is not None
            and isinstance(request_data, bytes)
            and headers is not None
            and "Content-Type" in headers
        ):
            request_kwargs["content_type"] = headers["Content-Type"]

        return request_data, request_kwargs

    async def _do_request(self, request: HttpRequest) -> Response:
        try:
            response = self.view(request)
        except Http404:
            return Response(status_code=404, data=b"Not found")
        except (BadRequest, SuspiciousOperation) as exc:
            return Response(status_code=400, data=str(exc).encode())

        return Response(
            status_code=response.status_code,
            data=response.content,
            headers=dict(response.headers),
        )

    async def request(
        self,
        url: str,
        method: str,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Response:
        cookies = kwargs.pop("cookies", None)
        files = kwargs.pop("files", None)
        data = kwargs.pop("data", None)
        json_data = kwargs.pop("json", None)

        merged_headers = merge_cookies(headers, cookies) or {}
        request_data, request_kwargs = self._build_request_data(
            data=data,
            json_data=json_data,
            files=files,
            headers=merged_headers,
        )
        request_kwargs.update(self._to_django_headers(merged_headers))
        request_kwargs.update(kwargs)

        request_factory = RequestFactory()
        request = getattr(request_factory, method)(
            url, data=request_data, **request_kwargs
        )
        if cookies is not None:
            request.COOKIES = dict(cookies)

        return await self._do_request(request)


class AsyncDjangoHttpClient(HttpClient):
    def __init__(self, view: Callable[[HttpRequest], Awaitable[HttpResponse]]) -> None:
        ensure_django_setup()
        self.view = view

    def _to_django_headers(self, headers: Mapping[str, str]) -> dict[str, str]:
        return {
            f"HTTP_{key.upper().replace('-', '_')}": value
            for key, value in headers.items()
        }

    def _build_request_data(
        self,
        data: RequestData | None,
        json_data: object | None,
        files: dict[str, UploadedFile] | None,
        headers: dict[str, str] | None,
    ) -> tuple[object | None, dict[str, Any]]:
        request_kwargs: dict[str, Any] = {}
        request_data: object | None = data

        if json_data is not None:
            request_data = dumps(json_data)
            request_kwargs["content_type"] = "application/json"

        if files:
            if request_data is not None and not isinstance(request_data, Mapping):
                raise TypeError("Django multipart requests require mapping form data")

            multipart_data = dict(request_data or {})
            for key, (filename, content, content_type) in files.items():
                multipart_data[key] = SimpleUploadedFile(
                    filename,
                    content,
                    content_type=content_type or "application/octet-stream",
                )
            request_data = multipart_data
        elif (
            request_data is not None
            and isinstance(request_data, bytes)
            and headers is not None
            and "Content-Type" in headers
        ):
            request_kwargs["content_type"] = headers["Content-Type"]

        return request_data, request_kwargs

    async def _do_request(self, request: HttpRequest) -> Response:
        try:
            response = await self.view(request)
        except Http404:
            return Response(status_code=404, data=b"Not found")
        except (BadRequest, SuspiciousOperation) as exc:
            return Response(status_code=400, data=str(exc).encode())

        data = response.content
        if isinstance(response, StreamingHttpResponse):
            content = response.streaming_content
            if isinstance(content, Iterable):
                data = b"".join(content)

        return Response(
            status_code=response.status_code,
            data=data,
            headers=dict(response.headers),
        )

    async def request(
        self,
        url: str,
        method: str,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Response:
        cookies = kwargs.pop("cookies", None)
        files = kwargs.pop("files", None)
        data = kwargs.pop("data", None)
        json_data = kwargs.pop("json", None)

        merged_headers = merge_cookies(headers, cookies) or {}
        request_data, request_kwargs = self._build_request_data(
            data=data,
            json_data=json_data,
            files=files,
            headers=merged_headers,
        )
        request_kwargs.update(self._to_django_headers(merged_headers))
        request_kwargs.update(kwargs)

        request_factory = AsyncRequestFactory()
        request = getattr(request_factory, method)(
            url, data=request_data, **request_kwargs
        )
        if cookies is not None:
            request.COOKIES = dict(cookies)

        return await self._do_request(request)
