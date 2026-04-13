---
title: Testing with Cross Web
description: Use request fakes for unit tests or framework clients for request-level integration tests.
section: Testing
order: 1
---

# Testing with Cross Web

Cross Web gives you two testing layers:

- `TestingRequestAdapter` for focused unit tests around request parsing logic.
- `cross_web.testing.clients` for request-level integration tests against supported frameworks without starting a real server.

## Create a synthetic request

Use `TestingRequestAdapter` when your code only needs an `AsyncHTTPRequest` and you want to control the input directly:

```python
from cross_web import AsyncHTTPRequest, TestingRequestAdapter


async def test_reads_json_payload():
    request = AsyncHTTPRequest(
        TestingRequestAdapter(
            method="POST",
            content_type="application/json",
            headers={"x-request-id": "req_123"},
            json={"name": "Ada"},
        )
    )

    assert request.method == "POST"
    assert await request.get_body() == b'{"name": "Ada"}'
```

This is the fastest option for unit tests around validation, content negotiation, or request normalization.

## Shortcut for simple form submissions

If you only need form fields, `AsyncHTTPRequest.from_form_data()` is faster to write:

```python
request = AsyncHTTPRequest.from_form_data({"email": "ada@example.com"})
form_data = await request.get_form_data()

assert form_data.get("email") == "ada@example.com"
```

## Request-level integration tests

Cross Web also ships framework-specific test clients under `cross_web.testing.clients`.

Import the shared testing types from `cross_web.testing` and import concrete clients from their framework module:

```python
from cross_web.testing import HttpClient, Response
from cross_web.testing.clients.starlette import StarletteHttpClient
```

Do not import concrete client classes from `cross_web.testing.clients` directly. That package only exports shared base types so importing it does not pull optional framework dependencies.

Every client exposes the same async surface:

- `await client.request(url, method, headers=None, **kwargs)`
- `await client.get(url, headers=None, **kwargs)`
- `await client.post(url, data=None, json=None, files=None, headers=None, **kwargs)`

The returned `Response` exposes:

- `response.status_code`
- `response.headers`
- `response.text`
- `response.json`

## Example: test a Starlette handler

```python
import json

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from cross_web import AsyncHTTPRequest
from cross_web.testing.clients.starlette import StarletteHttpClient


async def echo(request: Request) -> JSONResponse:
    http_request = AsyncHTTPRequest.from_starlette(request)
    body = await http_request.get_body()

    return JSONResponse(
        {
            "method": http_request.method,
            "query": dict(http_request.query_params),
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

## Available clients

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

## Framework notes

All client methods are async, including the wrappers around synchronous frameworks such as Flask and Django.

`files=` expects a mapping of field names to `(filename, content_bytes, content_type)` tuples.

`DjangoHttpClient` and `AsyncDjangoHttpClient` take a Django view callable, not a Django app object. Django should already be configured in your test environment.

`ChaliceHttpClient` supports JSON and raw body requests but does not support form data or file uploads.

## Useful knobs on `TestingRequestAdapter`

When you stay at the unit-test layer, `TestingRequestAdapter` lets you set:

- `method`
- `query_params`
- `headers`
- `content_type`
- `url`
- `cookies`
- `form_data`
- `json`
