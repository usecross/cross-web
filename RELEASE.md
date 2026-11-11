Release type: minor

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
