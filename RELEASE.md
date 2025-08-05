---
release type: patch
---

This release fixes an issue with the AioHTTP integration when handling multipart form data.

## Changes
- Fixed multipart form data processing in AioHTTP adapter to handle data on-demand instead of requiring pre-processing
- Added proper support for file uploads in multipart requests
- Exported `FormData` class from the main package for better type hints
