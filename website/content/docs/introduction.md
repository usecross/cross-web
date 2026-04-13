---
title: Introduction
description: What cross-web is and where it fits in a shared Python web stack.
section: Getting Started
order: 1
---

# Cross Web

Cross Web gives you a small, framework-agnostic layer for HTTP requests and responses in Python.

It is useful when your business logic needs to work across more than one web framework and you do not want to keep rewriting the same request parsing or response shaping code for each integration.

## What it covers

- `AsyncHTTPRequest` wraps async-capable request access behind one interface.
- Framework-specific adapters expose the same core request fields for frameworks that differ heavily at the edge.
- `Response` and `Cookie` let you describe a response in plain Python before converting it into a framework response object.
- `HTTPException` gives shared code a lightweight exception type for HTTP failures.
- `cross_web.testing` adds request fakes and framework test clients for reusable tests.

## Supported adapters

Cross Web currently ships adapters for:

- FastAPI and Starlette
- Flask
- Django
- Sanic
- Quart
- Litestar
- aiohttp
- Chalice

## A typical flow

```python
from fastapi import FastAPI, Request

from cross_web import AsyncHTTPRequest, Response

app = FastAPI()


@app.post("/contacts")
async def create_contact(request: Request):
    http_request = AsyncHTTPRequest.from_fastapi(request)
    form_data = await http_request.get_form_data()

    name = form_data.get("name")
    return Response.redirect(f"/contacts?created={name}").to_fastapi()
```

Cross Web is intentionally narrow in scope. It does not replace your framework router, dependency system, or middleware. It standardizes the request and response layer that your reusable code depends on.
