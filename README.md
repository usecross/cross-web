# Cross

**Write once, run everywhere** - A universal web framework adapter for Python that lets you write code once and use it across multiple web frameworks.

## Installation

```bash
uv add cross-web
```

```python
from cross_web import Response
```

## Overview

Cross provides a unified interface for common web framework operations, allowing you to write framework-agnostic code that can be easily adapted to work with FastAPI, Flask, Django, and other popular Python web frameworks.

## Testing

This project is in early development!
Cross also ships framework-specific test clients under `cross_web.testing.clients`.

Import a concrete client from its module:

```python
from cross_web.testing.clients.starlette import StarletteHttpClient
from cross_web.testing.clients.flask import FlaskHttpClient
from cross_web.testing.clients.django import DjangoHttpClient
```

Do not import client classes from `cross_web.testing.clients` directly. The package only exports the shared base types so importing it does not pull optional framework dependencies.

The shared testing API lives in `cross_web.testing`:

```python
from cross_web.testing import HttpClient, Response
```

Every concrete client exposes the same async interface:

- `await client.request(url, method, headers=None, **kwargs)`
- `await client.get(url, headers=None, **kwargs)`
- `await client.post(url, data=None, json=None, files=None, headers=None, **kwargs)`

`Response` exposes:

- `response.status_code`
- `response.headers`
- `response.text`
- `response.json`

### Example

```python
import json

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from cross_web.request._starlette import StarletteRequestAdapter
from cross_web.testing.clients.starlette import StarletteHttpClient


async def echo(request: Request) -> JSONResponse:
    adapter = StarletteRequestAdapter(request)
    body = await adapter.get_body()

    return JSONResponse(
        {
            "method": adapter.method,
            "query": dict(adapter.query_params),
            "body": json.loads(body.decode()),
        }
    )


app = Starlette(routes=[Route("/echo", echo, methods=["POST"])])


@pytest.mark.asyncio
async def test_echo() -> None:
    client = StarletteHttpClient(app)

    response = await client.post("/echo?debug=1", json={"hello": "world"})

    assert response.status_code == 200
    assert response.json == {
        "method": "POST",
        "query": {"debug": "1"},
        "body": {"hello": "world"},
    }
```

### Django

`DjangoHttpClient` and `AsyncDjangoHttpClient` take a Django view callable, not a Django app object.

Django must already be configured by your test environment. The recommended setup is `pytest-django` with a test settings module:

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "myproject.test_settings"
```

### Available clients

- `cross_web.testing.clients.aiohttp.AiohttpHttpClient`
- `cross_web.testing.clients.chalice.ChaliceHttpClient`
- `cross_web.testing.clients.django.DjangoHttpClient`
- `cross_web.testing.clients.django.AsyncDjangoHttpClient`
- `cross_web.testing.clients.flask.FlaskHttpClient`
- `cross_web.testing.clients.flask.AsyncFlaskHttpClient`
- `cross_web.testing.clients.litestar.LitestarHttpClient`
- `cross_web.testing.clients.quart.QuartHttpClient`
- `cross_web.testing.clients.sanic.SanicHttpClient`
- `cross_web.testing.clients.starlette.StarletteHttpClient`

### Notes

- All client methods are async, including clients wrapping sync frameworks.
- `files=` uses `(filename, content_bytes, content_type)` tuples.
- `ChaliceHttpClient` supports JSON requests but does not support form data or file uploads.
- The testing clients are intended for tests and integration-style handler checks, not as production HTTP clients.

## Documentation website

The repository now includes a Cross-Docs-powered website in [`website/`](website).

```bash
cd website
just setup
just dev
```

That setup uses `cross-docs` for the Python side, `@usecross/docs` on the frontend, the Inertia Vite plugin, and Inertia v3 packages.
