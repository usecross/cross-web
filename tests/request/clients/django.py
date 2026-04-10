from __future__ import annotations

import json

from .base import (
    FormRequestResult,
    JSONRequestResult,
    RequestClient,
    build_form_result,
    build_json_result,
)


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
        ROOT_URLCONF="tests.request.django_urls",
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

        with override_settings(ROOT_URLCONF="tests.request.django_urls"):
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

        with override_settings(ROOT_URLCONF="tests.request.django_urls"):
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

        with override_settings(ROOT_URLCONF="tests.request.django_urls"):
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

        with override_settings(ROOT_URLCONF="tests.request.django_urls"):
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
