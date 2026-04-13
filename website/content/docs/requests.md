---
title: Working with requests
description: Normalize request reading across different Python frameworks.
section: Requests
order: 1
---

# Working with requests

The request side of Cross Web is centered around adapter objects and the `AsyncHTTPRequest` convenience wrapper.

## Shared request fields

Every request adapter exposes the same core data:

- `method`
- `query_params`
- `headers`
- `content_type`
- `url`
- `cookies`

Async adapters also expose:

- `await get_body()`
- `await get_form_data()`

## Use `AsyncHTTPRequest` in shared code

```python
from fastapi import Request

from cross_web import AsyncHTTPRequest


async def read_payload(request: Request) -> bytes:
    http_request = AsyncHTTPRequest.from_fastapi(request)

    if http_request.content_type == "application/json":
        return await http_request.get_body()

    form_data = await http_request.get_form_data()
    return str(form_data.form).encode("utf-8")
```

`AsyncHTTPRequest` lets the rest of your code ignore the original framework once the request has been wrapped.

## Use direct adapters at framework boundaries

If you prefer explicit framework adapters, you can instantiate them directly:

```python
from flask import request

from cross_web import FlaskHTTPRequestAdapter


adapter = FlaskHTTPRequestAdapter(request)
user_agent = adapter.headers.get("user-agent")
```

This is useful when you want complete control over how the request object enters your shared code, or when you are dealing with a synchronous framework API.

## Form data

`get_form_data()` returns a `FormData` object with:

- `form` for regular fields
- `files` for uploaded files

The helper method `form_data.get("field_name")` reads from the regular form mapping.
