CHANGELOG
=========

0.8.0 - 2026-11-11
------------------

This release adds `parse_content_type`, a helper that parses a `Content-Type`
header value into its media type and a dictionary of parameters.

```python
from cross_web import parse_content_type

media_type, params = parse_content_type('Multipart/Form-Data; Boundary="a;b"')

assert media_type == "multipart/form-data"
assert params == {"boundary": "a;b"}
```

The media type and the parameter names are lowercased, quoted values are
unquoted, and the parsing is lenient, so it never raises on a malformed
header.

This release was contributed by [@patrick91](https://github.com/patrick91) in [#24](https://github.com/usecross/cross-web/pull/24)

0.7.1 - 2026-11-06
------------------

`Response.redirect` now merges `query_params` into a URL that already has a
query string instead of appending a second `?` to it, so
`Response.redirect("/cb?a=1", {"code": "x"})` redirects to `/cb?a=1&code=x`.
A fragment stays after the query, including an empty `#`, and a list value is
repeated as `key=a&key=b` rather than encoded as a Python list.

This release was contributed by [@patrick91](https://github.com/patrick91) in [#21](https://github.com/usecross/cross-web/pull/21)

0.7.0 - 2026-05-19
------------------

This release adds a synchronous `HTTPRequest` wrapper for sync request adapters.

0.6.0 - 2026-04-13
------------------

This release adds support for path params

0.5.0 - 2026-04-13
------------------

Add `cross_web.testing.clients`, a shared request-integration client matrix
for the supported frameworks.

This moves the reusable request test harnesses out of `tests/` and into a
package that other projects can import directly, including the Django test
URLConf needed by the client suite.

0.4.1 - 2026-01-09
------------------

Add missing metadata fields to pyproject.toml for improved PyPI discoverability:

- `license` field
- `keywords` for search
- `[project.urls]` with links to Homepage, Repository, Issues, and Changelog

0.4.0 - 2025-12-25
------------------

Renamed package from `lia-web` to `cross-web`. The import name is now `cross_web`.

```python
from cross_web import Response
```

If you were using `lia-web`, you can continue using it as a compatibility shim - it now depends on `cross-web` and re-exports all symbols. However, we recommend updating your imports to use `cross_web` directly.

0.2.3 - 2025-08-11
------------------

This release adds the MIT license for this project.

0.2.2 - 2025-08-08
------------------

This release removes Pydantic from the dependencies, since it was not used

0.2.1 - 2025-08-05
------------------

This release fixes an issue with the AioHTTP integration when handling multipart form data.

## Changes
- Fixed multipart form data processing in AioHTTP adapter to handle data on-demand instead of requiring pre-processing
- Added proper support for file uploads in multipart requests
- Exported `FormData` class from the main package for better type hints

0.2.0 - 2025-08-04
------------------

This release adds support for multiple new web frameworks and improves the testing infrastructure.

## New Features

- Added support for 6 new web frameworks:
  - aiohttp
  - Chalice (AWS)
  - Django
  - Flask
  - Quart
  - Sanic
- Added comprehensive test coverage for all new framework adapters
- Added protocols module for better type checking
- Added custom exceptions module

## Improvements

- Enhanced testing infrastructure with noxfile.py for multi-version testing
- Added pre-commit configuration for code quality
- Added GitHub Actions workflow for automated testing
- Improved type checking with dedicated test files
- Extended test coverage with additional test files for edge cases

## Development

- Updated pyproject.toml with new dependencies and configurations
- Improved project structure with better separation of concerns

0.1.2 - 2025-06-20
------------------

This release adds a readme file

0.1.1 - 2025-06-20
------------------

This is a test release