import re

_QUOTED_PAIR = re.compile(r"\\(.)", re.DOTALL)
_QUOTED_STRING = re.compile(r'"((?:[^"\\]|\\.)*)"', re.DOTALL)


def _split_parameters(value: str) -> list[str]:
    """Split on the `;` characters that are not inside a quoted string.

    A quoted string that is never closed runs to the end of the value.
    """
    segments: list[str] = []
    current: list[str] = []
    in_quotes = False
    escaped = False

    for char in value:
        if in_quotes:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_quotes = False
        elif char == '"':
            in_quotes = True
        elif char == ";":
            segments.append("".join(current))
            current = []
            continue

        current.append(char)

    segments.append("".join(current))

    return segments


def _unquote(value: str) -> str:
    """Return the content of a quoted string, with its escapes resolved.

    A value that is not one complete quoted string is returned unchanged,
    including one whose final quote is escaped and so never closes it.
    """
    if match := _QUOTED_STRING.fullmatch(value):
        return _QUOTED_PAIR.sub(r"\1", match.group(1))

    return value


def parse_content_type(content_type: str) -> tuple[str, dict[str, str]]:
    """Parse a `Content-Type` header value into a media type and its parameters.

    The media type and the parameter names are case-insensitive, so they are
    returned lowercased and can be compared exactly. Parameter values keep
    their case; a quoted value is returned without its quotes and with its
    backslash escapes resolved, so it may contain `;` and `"`.

    The parsing is lenient and never raises: surrounding whitespace is
    ignored, empty parameters are skipped, a parameter without `=` gets an
    empty value, and when a parameter is repeated the last value wins. An
    empty header gives an empty media type.

    Only the HTTP syntax is applied (RFC 9110, section 8.3.1). The parameter
    continuations and encoded values that e-mail headers have (RFC 2231) are
    not part of it, so a `*` in a parameter name is kept as part of the name.

    >>> parse_content_type('Multipart/Form-Data; Boundary="a;b"')
    ('multipart/form-data', {'boundary': 'a;b'})
    """
    media_type, *segments = _split_parameters(content_type)

    params: dict[str, str] = {}

    for segment in segments:
        name, _, value = segment.partition("=")
        name = name.strip().lower()

        if name:
            params[name] = _unquote(value.strip())

    return media_type.strip().lower(), params


__all__ = ["parse_content_type"]
