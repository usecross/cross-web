from __future__ import annotations

import json
import uuid
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit


def get_content_type(headers: Mapping[str, str]) -> str | None:
    for key, value in headers.items():
        if key.lower() == "content-type":
            return value

    return None


def normalize_cookies(cookies: Mapping[str, object]) -> dict[str, str]:
    normalized: dict[str, str] = {}

    for key, value in cookies.items():
        if isinstance(value, (list, tuple)) and len(value) == 1:
            normalized[str(key)] = str(value[0])
        else:
            normalized[str(key)] = str(value)

    return normalized


def unwrap_single_value(value: object) -> object:
    if isinstance(value, (list, tuple)) and len(value) == 1:
        return value[0]

    return value


def build_result(
    adapter: Any,
    *,
    body_json: object | None = None,
    form_value: object | None = None,
    has_file: bool | None = None,
    post_form_value: object | None = None,
    files_has_file: bool | None = None,
) -> dict[str, object]:
    url = urlsplit(str(adapter.url))
    result: dict[str, object] = {
        "query_params": dict(adapter.query_params),
        "method": adapter.method,
        "header_content_type": get_content_type(dict(adapter.headers)),
        "content_type": adapter.content_type,
        "url_path": url.path,
        "url_query": url.query,
        "cookies": normalize_cookies(dict(adapter.cookies)),
    }

    if body_json is not None:
        result["body_json"] = body_json

    if form_value is not None:
        result["form_value"] = unwrap_single_value(form_value)

    if has_file is not None:
        result["has_file"] = has_file

    if post_form_value is not None:
        result["post_form_value"] = unwrap_single_value(post_form_value)

    if files_has_file is not None:
        result["files_has_file"] = files_has_file

    return result


def create_aiohttp_app() -> Any:
    from aiohttp import web

    from cross_web.request._aiohttp import AiohttpHTTPRequestAdapter

    async def handler(request: web.Request) -> web.Response:
        adapter = await AiohttpHTTPRequestAdapter.create(request)

        if adapter.content_type == "application/json":
            body = await adapter.get_body()
            payload = build_result(adapter, body_json=json.loads(body.decode()))
        else:
            form_data = await adapter.get_form_data()
            payload = build_result(
                adapter,
                form_value=form_data.form["form"],
                has_file="file" in form_data.files,
            )

        return web.json_response(payload)

    app = web.Application()
    app.router.add_post("/request", handler)
    return app


def create_chalice_app() -> Any:
    from chalice.app import Chalice

    from cross_web.request._chalice import ChaliceHTTPRequestAdapter

    app = Chalice(app_name="cross-web-testing")

    @app.route("/request", methods=["POST"], content_types=["application/json"])
    def handler() -> dict[str, object]:
        request = app.current_request
        assert request is not None

        adapter = ChaliceHTTPRequestAdapter(request)
        return build_result(adapter, body_json=json.loads(adapter.body))

    return app


def create_django_view() -> Any:
    from django.http import HttpRequest, JsonResponse

    from cross_web.request._django import DjangoHTTPRequestAdapter

    def view(request: HttpRequest) -> JsonResponse:
        adapter = DjangoHTTPRequestAdapter(request)

        if adapter.content_type == "application/json":
            payload = build_result(adapter, body_json=json.loads(adapter.body))
        else:
            form_data = adapter.get_form_data()
            payload = build_result(
                adapter,
                form_value=form_data.form["form"],
                has_file="file" in form_data.files,
                post_form_value=adapter.post_data["form"],
                files_has_file="file" in adapter.files,
            )

        return JsonResponse(payload)

    return view


def create_async_django_view() -> Any:
    from django.http import HttpRequest, JsonResponse

    from cross_web.request._django import AsyncDjangoHTTPRequestAdapter

    async def view(request: HttpRequest) -> JsonResponse:
        adapter = AsyncDjangoHTTPRequestAdapter(request)

        if adapter.content_type == "application/json":
            body = await adapter.get_body()
            payload = build_result(adapter, body_json=json.loads(body.decode()))
        else:
            form_data = await adapter.get_form_data()
            payload = build_result(
                adapter,
                form_value=form_data.form["form"],
                has_file="file" in form_data.files,
            )

        return JsonResponse(payload)

    return view


def create_flask_app() -> Any:
    from flask import Flask, request

    from cross_web.request._flask import FlaskHTTPRequestAdapter

    app = Flask(__name__)

    @app.post("/request")
    def handler() -> dict[str, object]:
        adapter = FlaskHTTPRequestAdapter(request)

        if adapter.content_type == "application/json":
            return build_result(adapter, body_json=json.loads(adapter.body))

        form_data = adapter.get_form_data()
        return build_result(
            adapter,
            form_value=form_data.form["form"],
            has_file="file" in form_data.files,
            post_form_value=adapter.post_data["form"],
            files_has_file="file" in adapter.files,
        )

    return app


def create_async_flask_app() -> Any:
    from flask import Flask, request

    from cross_web.request._flask import AsyncFlaskHTTPRequestAdapter

    app = Flask(__name__)

    @app.post("/request")
    async def handler() -> dict[str, object]:
        adapter = AsyncFlaskHTTPRequestAdapter(request)

        if adapter.content_type == "application/json":
            body = await adapter.get_body()
            return build_result(adapter, body_json=json.loads(body.decode()))

        form_data = await adapter.get_form_data()
        return build_result(
            adapter,
            form_value=form_data.form["form"],
            has_file="file" in form_data.files,
        )

    return app


def create_litestar_app() -> Any:
    from litestar import Litestar, Request, post

    from cross_web.request._litestar import LitestarRequestAdapter

    @post("/request", status_code=200)
    async def handler(request: Request[Any, Any, Any]) -> dict[str, object]:
        adapter = LitestarRequestAdapter(request)

        if adapter.content_type == "application/json":
            body = await adapter.get_body()
            return build_result(adapter, body_json=json.loads(body.decode()))

        form_data = await adapter.get_form_data()
        return build_result(
            adapter,
            form_value=form_data.form["form"],
            has_file="file" in form_data.files,
        )

    return Litestar([handler])


def create_quart_app() -> Any:
    from quart import Quart, request

    from cross_web.request._quart import QuartHTTPRequestAdapter

    app = Quart(__name__)

    @app.post("/request")
    async def handler() -> dict[str, object]:
        adapter = QuartHTTPRequestAdapter(request)

        if adapter.content_type == "application/json":
            body = await adapter.get_body()
            return build_result(adapter, body_json=json.loads(body.decode()))

        form_data = await adapter.get_form_data()
        return build_result(
            adapter,
            form_value=form_data.form["form"],
            has_file="file" in form_data.files,
        )

    return app


def create_sanic_app() -> Any:
    from sanic import Sanic
    from sanic.request import Request
    from sanic.response import JSONResponse
    from sanic.response import json as sanic_json

    from cross_web.request._sanic import SanicHTTPRequestAdapter

    app = Sanic(f"CrossWeb_{uuid.uuid4().hex[:8]}")

    async def handler(request: Request) -> JSONResponse:
        adapter = SanicHTTPRequestAdapter(request)

        if adapter.content_type == "application/json":
            body = await adapter.get_body()
            payload = build_result(adapter, body_json=json.loads(body.decode()))
        else:
            form_data = await adapter.get_form_data()
            payload = build_result(
                adapter,
                form_value=form_data.form["form"],
                has_file="file" in form_data.files,
            )

        return sanic_json(payload)

    app.add_route(handler, "/request", methods=["POST"])
    return app


def create_starlette_app() -> Any:
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from starlette.routing import Route

    from cross_web.request._starlette import StarletteRequestAdapter

    async def handler(request: Request) -> JSONResponse:
        adapter = StarletteRequestAdapter(request)

        if adapter.content_type == "application/json":
            body = await adapter.get_body()
            payload = build_result(adapter, body_json=json.loads(body.decode()))
        else:
            form_data = await adapter.get_form_data()
            payload = build_result(
                adapter,
                form_value=form_data.form["form"],
                has_file="file" in form_data.files,
            )

        return JSONResponse(payload)

    return Starlette(routes=[Route("/request", handler, methods=["POST"])])
