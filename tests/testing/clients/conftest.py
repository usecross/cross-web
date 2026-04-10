import importlib
from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import Any, cast

import pytest

from cross_web.testing import HttpClient

from .builders import (
    create_aiohttp_app,
    create_async_django_view,
    create_async_flask_app,
    create_chalice_app,
    create_django_view,
    create_flask_app,
    create_litestar_app,
    create_quart_app,
    create_sanic_app,
    create_starlette_app,
)


@dataclass(frozen=True)
class HttpClientConfig:
    client_class: type[HttpClient]
    app_factory: Callable[[], object]


def _get_http_client_configs() -> Generator[Any, None, None]:
    for client, module, app_factory, marks in [
        ("AiohttpHttpClient", "aiohttp", create_aiohttp_app, [pytest.mark.aiohttp]),
        ("ChaliceHttpClient", "chalice", create_chalice_app, [pytest.mark.chalice]),
        (
            "AsyncDjangoHttpClient",
            "django",
            create_async_django_view,
            [pytest.mark.django],
        ),
        ("DjangoHttpClient", "django", create_django_view, [pytest.mark.django]),
        (
            "AsyncFlaskHttpClient",
            "flask",
            create_async_flask_app,
            [pytest.mark.flask],
        ),
        ("FlaskHttpClient", "flask", create_flask_app, [pytest.mark.flask]),
        ("LitestarHttpClient", "litestar", create_litestar_app, [pytest.mark.litestar]),
        ("QuartHttpClient", "quart", create_quart_app, [pytest.mark.quart]),
        ("SanicHttpClient", "sanic", create_sanic_app, [pytest.mark.sanic]),
        (
            "StarletteHttpClient",
            "starlette",
            create_starlette_app,
            [pytest.mark.starlette],
        ),
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
            None
            if client_class is None
            else HttpClientConfig(client_class, app_factory),
            marks=[
                *marks,
                pytest.mark.skipif(
                    client_class is None, reason=f"Client {client} not found"
                ),
            ],
        )


@pytest.fixture(params=_get_http_client_configs())
def http_client_config(request: Any) -> HttpClientConfig:
    return cast(HttpClientConfig, request.param)


@pytest.fixture
def http_client(http_client_config: HttpClientConfig) -> HttpClient:
    return http_client_config.client_class(http_client_config.app_factory())
