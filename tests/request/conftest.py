import importlib
from collections.abc import Generator
from typing import Any

import pytest

from cross_web.testing.clients.base import RequestClient


def _get_request_client_classes() -> Generator[Any, None, None]:
    for client, module, marks in [
        ("AiohttpRequestClient", "aiohttp", [pytest.mark.aiohttp]),
        ("ChaliceRequestClient", "chalice", [pytest.mark.chalice]),
        ("AsyncDjangoRequestClient", "django", [pytest.mark.django]),
        ("DjangoRequestClient", "django", [pytest.mark.django]),
        ("AsyncFlaskRequestClient", "flask", [pytest.mark.flask]),
        ("FlaskRequestClient", "flask", [pytest.mark.flask]),
        ("LitestarRequestClient", "litestar", [pytest.mark.litestar]),
        ("QuartRequestClient", "quart", [pytest.mark.quart]),
        ("SanicRequestClient", "sanic", [pytest.mark.sanic]),
        ("StarletteRequestClient", "starlette", [pytest.mark.starlette]),
    ]:
        try:
            client_class = getattr(
                importlib.import_module(
                    f".{module}", package="cross_web.testing.clients"
                ),
                client,
            )
        except ImportError:
            client_class = None

        yield pytest.param(
            client_class,
            marks=[
                *marks,
                pytest.mark.skipif(
                    client_class is None, reason=f"Client {client} not found"
                ),
            ],
        )


@pytest.fixture(params=_get_request_client_classes())
def request_client_class(request: Any) -> type[RequestClient]:
    return request.param


@pytest.fixture
def request_client(request_client_class: type[RequestClient]) -> RequestClient:
    return request_client_class()
