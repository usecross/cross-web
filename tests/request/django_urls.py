from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.urls import path

from cross_web import AsyncDjangoHTTPRequestAdapter, DjangoHTTPRequestAdapter


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
