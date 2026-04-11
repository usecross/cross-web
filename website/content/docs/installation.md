---
title: Installation
description: Install cross-web and understand the runtime expectations around framework integrations.
section: Getting Started
order: 2
---

# Installation

Install Cross Web with your preferred Python package manager:

```bash
uv add cross-web
```

```bash
pip install cross-web
```

The base package is small. Your actual web framework stays an application dependency, and Cross Web adapts to the request object you hand it.

## Import the public API

```python
from cross_web import AsyncHTTPRequest, Cookie, HTTPException, Response
```

If you want direct access to a specific adapter, those are also exported from the package root:

```python
from cross_web import FlaskHTTPRequestAdapter, StarletteRequestAdapter
```

## Pick the right abstraction

Use `AsyncHTTPRequest` when you want a shared async-friendly interface that can be created from framework request objects:

- `AsyncHTTPRequest.from_fastapi(...)`
- `AsyncHTTPRequest.from_starlette(...)`
- `AsyncHTTPRequest.from_django(...)`
- `AsyncHTTPRequest.from_flask(...)`
- `AsyncHTTPRequest.from_sanic(...)`
- `AsyncHTTPRequest.from_aiohttp(...)`
- `AsyncHTTPRequest.from_quart(...)`
- `AsyncHTTPRequest.from_litestar(...)`

Use direct adapters when you need framework-specific entry points or synchronous request access, such as:

- `DjangoHTTPRequestAdapter`
- `FlaskHTTPRequestAdapter`
- `ChaliceHTTPRequestAdapter`

## Framework dependencies

Cross Web does not install every supported framework for you. Your project should already depend on the framework you are integrating with, plus any form parsing or testing extras that framework requires.
