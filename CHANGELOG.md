CHANGELOG
=========

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