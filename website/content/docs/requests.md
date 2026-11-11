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
- `client_host`

Async adapters also expose:

- `await get_body()`
- `await get_form_data()`

## Client address

`client_host` is the client's address as the framework reports it, or `None`
when the framework doesn't know it. Cross Web doesn't read `X-Forwarded-For`
itself: behind a proxy, set up your server to trust the proxy's forwarded
headers (for example `uvicorn --proxy-headers` or Werkzeug's `ProxyFix`), or
`client_host` is the proxy's address.

Test clients report their own placeholder, such as `127.0.0.1` or `testclient`,
so don't expect an IP address in tests.

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

## Parse the content type

`content_type` is the raw header value, so it can carry parameters such as `charset` or `boundary` and can be written in any case. `parse_content_type` splits it into a media type and a dictionary of parameters:

```python
from cross_web import parse_content_type

media_type, params = parse_content_type("Application/JSON; charset=utf-8")

assert media_type == "application/json"
assert params == {"charset": "utf-8"}
```

The media type and the parameter names are lowercased, so they can be compared exactly. Quoted parameter values are returned without their quotes. The parsing is lenient and never raises: a malformed header gives whatever could be read from it, and an empty one gives an empty media type, so pass `request.content_type or ""` when the header may be missing.

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
