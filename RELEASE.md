---
release type: minor
---

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
