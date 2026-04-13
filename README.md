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

## Features

This project is in early development!

## Documentation website

The repository now includes a Cross-Docs-powered website in [`website/`](website).

```bash
cd website
just setup
just dev
```

That setup uses `cross-docs` for the Python side, `@usecross/docs` on the frontend, the Inertia Vite plugin, and Inertia v3 packages.
