---
title: Working with responses
description: Use portable response objects before converting them into framework responses.
section: Responses
order: 1
---

# Working with responses

`Response` is a plain dataclass that keeps status, body, cookies, and headers together in one portable object.

## Build a response directly

```python
from cross_web import Cookie, Response

response = Response(
    status_code=201,
    body='{"created": true}',
    headers={"content-type": "application/json"},
    cookies=[
        Cookie(name="session", value="abc123", secure=True),
    ],
)
```

## Redirects

Use `Response.redirect()` when you want a standard 302 response with optional query params, headers, or cookies:

```python
from cross_web import Response

response = Response.redirect(
    "/login",
    query_params={"next": "/settings"},
    headers={"x-flow": "auth"},
)
```

## Reading JSON bodies

If a response body contains JSON, `response.json()` will deserialize it for you:

```python
payload = response.json()
```

## FastAPI conversion

Cross Web currently includes a built-in converter for FastAPI:

```python
fastapi_response = response.to_fastapi()
```

That keeps your shared code framework-agnostic while still giving your FastAPI routes a native response object at the edge.
