from __future__ import annotations

import pytest
from unittest.mock import Mock

from cross_web._apply_cookie import apply_cookie
from cross_web.response import Cookie


def _make_cookie(**overrides: object) -> Cookie:
    defaults = dict(
        name="session",
        value="abc123",
        secure=True,
        path="/api",
        domain="example.com",
        max_age=3600,
        httponly=True,
        samesite="strict",
    )
    defaults.update(overrides)
    return Cookie(**defaults)  # type: ignore[arg-type]


# --- Unsupported type ---


def test_unsupported_type_raises_type_error() -> None:
    cookie = _make_cookie()

    with pytest.raises(TypeError, match="Unsupported response type"):
        cookie.apply("not a response")


def test_apply_cookie_standalone_raises_for_unsupported() -> None:
    cookie = _make_cookie()

    with pytest.raises(TypeError, match="Unsupported response type"):
        apply_cookie(42, cookie)


# --- Starlette / FastAPI ---


@pytest.mark.starlette
def test_apply_to_starlette() -> None:
    from starlette.responses import Response

    response = Response()
    cookie = _make_cookie()

    cookie.apply(response)

    set_cookie_header = response.headers.get("set-cookie", "")
    assert "session=abc123" in set_cookie_header


@pytest.mark.starlette
def test_apply_to_starlette_mock() -> None:
    from starlette.responses import Response

    response = Mock(spec=Response)
    cookie = _make_cookie()

    cookie.apply(response)

    response.set_cookie.assert_called_once_with(
        key="session",
        value="abc123",
        secure=True,
        path="/api",
        domain="example.com",
        max_age=3600,
        httponly=True,
        samesite="strict",
    )


@pytest.mark.fastapi
def test_apply_to_fastapi_response() -> None:
    from fastapi import Response

    response = Mock(spec=Response)
    cookie = _make_cookie()

    cookie.apply(response)

    response.set_cookie.assert_called_once_with(
        key="session",
        value="abc123",
        secure=True,
        path="/api",
        domain="example.com",
        max_age=3600,
        httponly=True,
        samesite="strict",
    )


# --- Django ---


@pytest.mark.django
def test_apply_to_django() -> None:
    from django.http import HttpResponse

    response = Mock(spec=HttpResponse)
    cookie = _make_cookie()

    cookie.apply(response)

    response.set_cookie.assert_called_once_with(
        key="session",
        value="abc123",
        max_age=3600,
        path="/api",
        domain="example.com",
        secure=True,
        httponly=True,
        samesite="strict",
    )


# --- Flask (Werkzeug) ---


@pytest.mark.flask
def test_apply_to_flask() -> None:
    from flask import Response

    response = Mock(spec=Response)
    cookie = _make_cookie()

    cookie.apply(response)

    response.set_cookie.assert_called_once_with(
        key="session",
        value="abc123",
        max_age=3600,
        path="/api",
        domain="example.com",
        secure=True,
        httponly=True,
        samesite="strict",
    )


# --- Quart ---


@pytest.mark.quart
def test_apply_to_quart() -> None:
    from quart import Response

    response = Mock(spec=Response)
    cookie = _make_cookie()

    cookie.apply(response)

    response.set_cookie.assert_called_once_with(
        key="session",
        value="abc123",
        max_age=3600,
        path="/api",
        domain="example.com",
        secure=True,
        httponly=True,
        samesite="strict",
    )


# --- Sanic ---


@pytest.mark.sanic
def test_apply_to_sanic() -> None:
    from sanic.response import BaseHTTPResponse

    response = Mock(spec=BaseHTTPResponse)
    cookie = _make_cookie()

    cookie.apply(response)

    # Sanic uses add_cookie, not set_cookie
    response.add_cookie.assert_called_once_with(
        "session",
        "abc123",
        path="/api",
        domain="example.com",
        secure=True,
        max_age=3600,
        httponly=True,
        samesite="strict",
    )


# --- aiohttp ---


@pytest.mark.aiohttp
def test_apply_to_aiohttp() -> None:
    from aiohttp.web import StreamResponse

    response = Mock(spec=StreamResponse)
    cookie = _make_cookie()

    cookie.apply(response)

    # aiohttp uses name= instead of key=
    response.set_cookie.assert_called_once_with(
        name="session",
        value="abc123",
        path="/api",
        domain="example.com",
        max_age=3600,
        secure=True,
        httponly=True,
        samesite="strict",
    )


# --- Litestar ---


@pytest.mark.litestar
def test_apply_to_litestar() -> None:
    from litestar.response import Response

    response = Mock(spec=Response)
    cookie = _make_cookie()

    cookie.apply(response)

    response.set_cookie.assert_called_once_with(
        key="session",
        value="abc123",
        max_age=3600,
        path="/api",
        domain="example.com",
        secure=True,
        httponly=True,
        samesite="strict",
    )


# --- Chalice ---


@pytest.mark.chalice
def test_apply_to_chalice() -> None:
    from chalice.app import Response

    response = Response(body="", headers={}, status_code=200)
    cookie = _make_cookie()

    cookie.apply(response)

    header = response.headers["Set-Cookie"]
    assert header == (
        "session=abc123; Path=/api; Domain=example.com; "
        "Max-Age=3600; Secure; HttpOnly; SameSite=strict"
    )


@pytest.mark.chalice
def test_apply_to_chalice_minimal_cookie() -> None:
    from chalice.app import Response

    response = Response(body="", headers={}, status_code=200)
    cookie = Cookie(name="simple", value="val", secure=False, httponly=False)

    cookie.apply(response)

    header = response.headers["Set-Cookie"]
    assert header == "simple=val; SameSite=lax"


@pytest.mark.chalice
def test_apply_to_chalice_none_headers() -> None:
    from chalice.app import Response

    response = Response(body="", status_code=200)
    response.headers = None  # type: ignore[assignment]
    cookie = _make_cookie()

    cookie.apply(response)

    assert response.headers["Set-Cookie"] is not None


# --- Standalone function ---


@pytest.mark.starlette
def test_standalone_apply_cookie() -> None:
    from starlette.responses import Response

    response = Mock(spec=Response)
    cookie = _make_cookie()

    apply_cookie(response, cookie)

    response.set_cookie.assert_called_once()


# --- Cookie with defaults ---


@pytest.mark.starlette
def test_apply_cookie_with_defaults() -> None:
    from starlette.responses import Response

    response = Mock(spec=Response)
    cookie = Cookie(name="minimal", value="v", secure=False)

    cookie.apply(response)

    response.set_cookie.assert_called_once_with(
        key="minimal",
        value="v",
        secure=False,
        path=None,
        domain=None,
        max_age=None,
        httponly=True,
        samesite="lax",
    )
