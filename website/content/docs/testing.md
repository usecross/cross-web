---
title: Testing shared request logic
description: Exercise request-handling code without booting a real application server.
section: Testing
order: 1
---

# Testing shared request logic

Cross Web includes `TestingRequestAdapter` so your tests can build request objects with only the fields you care about.

## Create a test request

```python
from cross_web.request import AsyncHTTPRequest
from cross_web.request._testing import TestingRequestAdapter


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

## Shortcut for form submissions

If you only need form fields, `AsyncHTTPRequest.from_form_data()` is faster to write:

```python
request = AsyncHTTPRequest.from_form_data({"email": "ada@example.com"})
form_data = await request.get_form_data()

assert form_data.get("email") == "ada@example.com"
```

## Useful knobs

`TestingRequestAdapter` lets you set:

- `method`
- `query_params`
- `headers`
- `content_type`
- `url`
- `cookies`
- `form_data`
- `json`

That makes it a good fit for unit tests around validation, content negotiation, or request normalization logic.
