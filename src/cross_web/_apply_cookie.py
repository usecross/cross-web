from __future__ import annotations

from functools import singledispatch
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .response import Cookie


@singledispatch
def apply_cookie(response: Any, cookie: Cookie) -> None:
    """Apply a cross_web Cookie to a framework-native response object.

    Dispatches based on the response type. Supports: Starlette/FastAPI,
    Django, Flask, Quart, Sanic, aiohttp, Litestar, and Chalice.
    """
    raise TypeError(f"Unsupported response type: {type(response)}")


# --- Starlette (covers FastAPI) ---

try:
    from starlette.responses import Response as StarletteResponse

    @apply_cookie.register(StarletteResponse)
    def _apply_starlette(response: Any, cookie: Cookie) -> None:
        response.set_cookie(
            key=cookie.name,
            value=cookie.value,
            secure=cookie.secure,
            path=cookie.path,
            domain=cookie.domain,
            max_age=cookie.max_age,
            httponly=cookie.httponly,
            samesite=cookie.samesite,
        )

except ImportError:
    pass


# --- Django ---

try:
    from django.http import HttpResponseBase as DjangoResponseBase

    @apply_cookie.register(DjangoResponseBase)
    def _apply_django(response: Any, cookie: Cookie) -> None:
        response.set_cookie(
            key=cookie.name,
            value=cookie.value,
            max_age=cookie.max_age,
            path=cookie.path,
            domain=cookie.domain,
            secure=cookie.secure,
            httponly=cookie.httponly,
            samesite=cookie.samesite,
        )

except ImportError:
    pass


# --- Werkzeug (covers Flask + Quart) ---

try:
    from werkzeug.sansio.response import Response as WerkzeugResponse

    @apply_cookie.register(WerkzeugResponse)
    def _apply_werkzeug(response: Any, cookie: Cookie) -> None:
        response.set_cookie(
            key=cookie.name,
            value=cookie.value,
            max_age=cookie.max_age,
            path=cookie.path,
            domain=cookie.domain,
            secure=cookie.secure,
            httponly=cookie.httponly,
            samesite=cookie.samesite,
        )

except ImportError:
    pass


# --- Sanic ---

try:
    from sanic.response import BaseHTTPResponse as SanicResponseBase

    @apply_cookie.register(SanicResponseBase)
    def _apply_sanic(response: Any, cookie: Cookie) -> None:
        response.add_cookie(
            cookie.name,
            cookie.value,
            path=cookie.path,
            domain=cookie.domain,
            secure=cookie.secure,
            max_age=cookie.max_age,
            httponly=cookie.httponly,
            samesite=cookie.samesite,
        )

except ImportError:
    pass


# --- aiohttp ---

try:
    from aiohttp.web import StreamResponse as AiohttpStreamResponse

    @apply_cookie.register(AiohttpStreamResponse)
    def _apply_aiohttp(response: Any, cookie: Cookie) -> None:
        response.set_cookie(
            name=cookie.name,
            value=cookie.value,
            path=cookie.path,
            domain=cookie.domain,
            max_age=cookie.max_age,
            secure=cookie.secure,
            httponly=cookie.httponly,
            samesite=cookie.samesite,
        )

except ImportError:
    pass


# --- Litestar ---

try:
    from litestar.response import Response as LitestarResponse

    @apply_cookie.register(LitestarResponse)
    def _apply_litestar(response: Any, cookie: Cookie) -> None:
        response.set_cookie(
            key=cookie.name,
            value=cookie.value,
            max_age=cookie.max_age,
            path=cookie.path,
            domain=cookie.domain,
            secure=cookie.secure,
            httponly=cookie.httponly,
            samesite=cookie.samesite,
        )

except ImportError:
    pass


# --- Chalice ---
# Chalice has no set_cookie API. Cookies are set via the Set-Cookie header.
# Limitation: Chalice uses a plain dict for headers, so multiple cookies
# will overwrite each other. This is a known Chalice limitation.

try:
    from chalice.app import Response as ChaliceResponse

    @apply_cookie.register(ChaliceResponse)
    def _apply_chalice(response: Any, cookie: Cookie) -> None:
        parts: list[str] = [f"{cookie.name}={cookie.value}"]

        if cookie.path is not None:
            parts.append(f"Path={cookie.path}")
        if cookie.domain is not None:
            parts.append(f"Domain={cookie.domain}")
        if cookie.max_age is not None:
            parts.append(f"Max-Age={cookie.max_age}")
        if cookie.secure:
            parts.append("Secure")
        if cookie.httponly:
            parts.append("HttpOnly")
        if cookie.samesite:
            parts.append(f"SameSite={cookie.samesite}")

        if response.headers is None:
            response.headers = {}
        response.headers["Set-Cookie"] = "; ".join(parts)

except ImportError:
    pass
