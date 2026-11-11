from __future__ import annotations

from typing import Any, Callable, Optional
from unittest.mock import Mock

import pytest

from cross_web.request._aiohttp import AiohttpHTTPRequestAdapter
from cross_web.request._django import (
    AsyncDjangoHTTPRequestAdapter,
    DjangoHTTPRequestAdapter,
)
from cross_web.request._flask import (
    AsyncFlaskHTTPRequestAdapter,
    FlaskHTTPRequestAdapter,
)
from cross_web.request._litestar import LitestarRequestAdapter
from cross_web.request._quart import QuartHTTPRequestAdapter
from cross_web.request._sanic import SanicHTTPRequestAdapter
from cross_web.request._starlette import StarletteRequestAdapter


def _client(host: Optional[str]) -> Optional[Mock]:
    return None if host is None else Mock(host=host)


# Each adapter and how its framework's request reports the client address.
ADAPTERS: list[tuple[Callable[[Any], Any], Callable[[Optional[str]], Mock]]] = [
    (StarletteRequestAdapter, lambda host: Mock(client=_client(host))),
    (LitestarRequestAdapter, lambda host: Mock(client=_client(host))),
    (
        DjangoHTTPRequestAdapter,
        lambda host: Mock(META={} if host is None else {"REMOTE_ADDR": host}),
    ),
    (
        AsyncDjangoHTTPRequestAdapter,
        lambda host: Mock(META={} if host is None else {"REMOTE_ADDR": host}),
    ),
    (FlaskHTTPRequestAdapter, lambda host: Mock(remote_addr=host)),
    (AsyncFlaskHTTPRequestAdapter, lambda host: Mock(remote_addr=host)),
    (QuartHTTPRequestAdapter, lambda host: Mock(remote_addr=host)),
    (AiohttpHTTPRequestAdapter, lambda host: Mock(remote=host)),
    # Sanic reports an unknown address as "".
    (SanicHTTPRequestAdapter, lambda host: Mock(client_ip=host or "")),
]


@pytest.mark.parametrize(("adapter_class", "make_request"), ADAPTERS)
def test_client_host_is_the_framework_client_address(
    adapter_class: Callable[[Any], Any], make_request: Callable[[Optional[str]], Mock]
) -> None:
    adapter = adapter_class(make_request("203.0.113.7"))

    assert adapter.client_host == "203.0.113.7"


@pytest.mark.parametrize(("adapter_class", "make_request"), ADAPTERS)
def test_client_host_is_none_when_the_framework_does_not_know_it(
    adapter_class: Callable[[Any], Any], make_request: Callable[[Optional[str]], Mock]
) -> None:
    adapter = adapter_class(make_request(None))

    assert adapter.client_host is None
