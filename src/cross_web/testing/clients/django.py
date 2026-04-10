from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.urls import path

from cross_web.request._django import (
    AsyncDjangoHTTPRequestAdapter,
    DjangoHTTPRequestAdapter,
)

from .base import (
    FormRequestResult,
    JSONRequestResult,
    RequestClient,
    build_form_result,
    build_json_result,
)


def sync_form_view(request: HttpRequest, item_id: str) -> JsonResponse:
    adapter = DjangoHTTPRequestAdapter(request)
    form_data = adapter.get_form_data()

    return JsonResponse(
        {
            "query_params": dict(adapter.query_params),
            "method": adapter.method,
            "header_content_type": adapter.headers["Content-Type"],
            "content_type": adapter.content_type,
            "url": adapter.url,
            "cookies": dict(adapter.cookies),
            "form_value": form_data.form["form"],
            "has_file": "file" in form_data.files,
            "post_form_value": adapter.post_data["form"],
            "files_has_file": "file" in adapter.files,
        }
    )


def sync_json_view(request: HttpRequest, item_id: str) -> JsonResponse:
    adapter = DjangoHTTPRequestAdapter(request)

    return JsonResponse(
        {
            "query_params": dict(adapter.query_params),
            "body_json": json.loads(adapter.body),
            "method": adapter.method,
            "header_content_type": adapter.headers["Content-Type"],
            "content_type": adapter.content_type,
            "url": adapter.url,
            "cookies": dict(adapter.cookies),
        }
    )


async def async_form_view(request: HttpRequest, item_id: str) -> JsonResponse:
    adapter = AsyncDjangoHTTPRequestAdapter(request)
    form_data = await adapter.get_form_data()

    return JsonResponse(
        {
            "query_params": dict(adapter.query_params),
            "method": adapter.method,
            "header_content_type": adapter.headers["Content-Type"],
            "content_type": adapter.content_type,
            "url": adapter.url,
            "cookies": dict(adapter.cookies),
            "form_value": form_data.form["form"],
            "has_file": "file" in form_data.files,
        }
    )


async def async_json_view(request: HttpRequest, item_id: str) -> JsonResponse:
    adapter = AsyncDjangoHTTPRequestAdapter(request)
    body = await adapter.get_body()

    return JsonResponse(
        {
            "query_params": dict(adapter.query_params),
            "body_json": json.loads(body.decode()),
            "method": adapter.method,
            "header_content_type": adapter.headers["Content-Type"],
            "content_type": adapter.content_type,
            "url": adapter.url,
            "cookies": dict(adapter.cookies),
        }
    )


urlpatterns = [
    path("sync/form/<str:item_id>", sync_form_view),
    path("sync/json/<str:item_id>", sync_json_view),
    path("async/form/<str:item_id>", async_form_view),
    path("async/json/<str:item_id>", async_json_view),
]


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
        ROOT_URLCONF="cross_web.testing.clients.django",
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
    )
    django.setup()


class DjangoRequestClient(RequestClient):
    def __init__(self) -> None:
        ensure_django_setup()

    async def json_request(self) -> JSONRequestResult:
        from django.test import Client, override_settings

        client = Client()
        client.cookies["session"] = "123"

        with override_settings(ROOT_URLCONF="cross_web.testing.clients.django"):
            response = client.post(
                "/sync/json/abc?query=test",
                data=json.dumps({"key": "value"}),
                content_type="application/json",
            )

        return build_json_result(response.json())

    async def form_request(self) -> FormRequestResult:
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import Client, override_settings

        client = Client()
        client.cookies["session"] = "123"

        with override_settings(ROOT_URLCONF="cross_web.testing.clients.django"):
            response = client.post(
                "/sync/form/abc?query=test",
                data={
                    "form": "data",
                    "file": SimpleUploadedFile(
                        "test.txt", b"upload", content_type="text/plain"
                    ),
                },
            )

        return build_form_result(response.json())


class AsyncDjangoRequestClient(RequestClient):
    def __init__(self) -> None:
        ensure_django_setup()

    async def json_request(self) -> JSONRequestResult:
        from django.test import AsyncClient, override_settings

        client = AsyncClient()
        client.cookies["session"] = "123"

        with override_settings(ROOT_URLCONF="cross_web.testing.clients.django"):
            response = await client.post(
                "/async/json/abc?query=test",
                data=json.dumps({"key": "value"}),
                content_type="application/json",
            )

        return build_json_result(response.json())

    async def form_request(self) -> FormRequestResult:
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.test import AsyncClient, override_settings

        client = AsyncClient()
        client.cookies["session"] = "123"

        with override_settings(ROOT_URLCONF="cross_web.testing.clients.django"):
            response = await client.post(
                "/async/form/abc?query=test",
                data={
                    "form": "data",
                    "file": SimpleUploadedFile(
                        "test.txt", b"upload", content_type="text/plain"
                    ),
                },
            )

        return build_form_result(response.json())
