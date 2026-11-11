import pytest
from cross_web import parse_content_type


@pytest.mark.parametrize(
    ("content_type", "expected"),
    [
        ("application/json", ("application/json", {})),
        ("text/html; charset=utf-8", ("text/html", {"charset": "utf-8"})),
        (
            "multipart/form-data; boundary=foobar; charset=utf-8",
            ("multipart/form-data", {"boundary": "foobar", "charset": "utf-8"}),
        ),
        (
            "multipart/form-data; charset=utf-8; boundary=foobar; foo=bar",
            (
                "multipart/form-data",
                {"charset": "utf-8", "boundary": "foobar", "foo": "bar"},
            ),
        ),
    ],
)
def test_parses_media_type_and_parameters(
    content_type: str, expected: tuple[str, dict[str, str]]
) -> None:
    assert parse_content_type(content_type) == expected


def test_media_type_and_parameter_names_are_lowercased() -> None:
    assert parse_content_type("Application/JSON; Charset=UTF-8") == (
        "application/json",
        {"charset": "UTF-8"},
    )


@pytest.mark.parametrize(
    "content_type",
    [
        " application/json ; charset=utf-8 ",
        "application/json;charset=utf-8",
        "application/json\t;\tcharset = utf-8",
    ],
)
def test_surrounding_whitespace_is_ignored(content_type: str) -> None:
    assert parse_content_type(content_type) == (
        "application/json",
        {"charset": "utf-8"},
    )


@pytest.mark.parametrize(
    ("content_type", "expected"),
    [
        ('multipart/mixed; boundary="graphql"', {"boundary": "graphql"}),
        ('multipart/mixed; boundary="a;b"; x=1', {"boundary": "a;b", "x": "1"}),
        ('multipart/mixed; boundary="a=b"', {"boundary": "a=b"}),
        ('multipart/mixed; boundary=" a b "', {"boundary": " a b "}),
        ('multipart/mixed; boundary=""', {"boundary": ""}),
        ('multipart/mixed; x="say \\"hi\\""', {"x": 'say "hi"'}),
        ('multipart/mixed; x="back\\\\slash"', {"x": "back\\slash"}),
        ('multipart/mixed; x="a\\\\\\"b"', {"x": 'a\\"b'}),
        ('multipart/mixed; x="\\a\\;"; y=1', {"x": "a;", "y": "1"}),
        ('multipart/mixed; x="a\\\\"; y=1', {"x": "a\\", "y": "1"}),
    ],
)
def test_quoted_parameter_values(content_type: str, expected: dict[str, str]) -> None:
    assert parse_content_type(content_type) == ("multipart/mixed", expected)


@pytest.mark.parametrize(
    ("content_type", "expected"),
    [
        ("", ("", {})),
        ("   ", ("", {})),
        (";", ("", {})),
        ("; charset=utf-8", ("", {"charset": "utf-8"})),
        ("application/json;", ("application/json", {})),
        ("application/json;; ;", ("application/json", {})),
        ("application/json; charset", ("application/json", {"charset": ""})),
        ("application/json; charset=", ("application/json", {"charset": ""})),
        ("application/json; =utf-8", ("application/json", {})),
        ("application/json; a=b=c", ("application/json", {"a": "b=c"})),
    ],
)
def test_empty_and_missing_values(
    content_type: str, expected: tuple[str, dict[str, str]]
) -> None:
    assert parse_content_type(content_type) == expected


def test_last_duplicate_parameter_wins() -> None:
    assert parse_content_type("text/plain; charset=a; Charset=b; x=1") == (
        "text/plain",
        {"charset": "b", "x": "1"},
    )


@pytest.mark.parametrize(
    ("content_type", "expected"),
    [
        ("text/plain; title*=utf-8''caf%C3%A9", {"title*": "utf-8''caf%C3%A9"}),
        ("text/plain; a*0=b; a*1=c", {"a*0": "b", "a*1": "c"}),
        ("text/plain; a*0*=b", {"a*0*": "b"}),
        ("text/plain; a*" + "1" * 5000 + "=b", {"a*" + "1" * 5000: "b"}),
        ("text/plain; *=b", {"*": "b"}),
    ],
)
def test_asterisk_is_part_of_the_parameter_name(
    content_type: str, expected: dict[str, str]
) -> None:
    assert parse_content_type(content_type) == ("text/plain", expected)


@pytest.mark.parametrize(
    ("content_type", "expected"),
    [
        # a quoted string that is never closed runs to the end of the value
        ('text/plain; a="open; b=1', ("text/plain", {"a": '"open; b=1'})),
        # an escaped final quote does not close the quoted string either
        ('text/plain; a="open\\"', ("text/plain", {"a": '"open\\"'})),
        ('text/plain; a="closed\\\\"', ("text/plain", {"a": "closed\\"})),
        ('text/plain; a="', ("text/plain", {"a": '"'})),
        ('text/plain; a="trailing\\', ("text/plain", {"a": '"trailing\\'})),
        # only a value that is quoted as a whole is unquoted
        ('text/plain; a="1.0", b', ("text/plain", {"a": '"1.0", b'})),
        ('text/plain; a=b"c;d"', ("text/plain", {"a": 'b"c;d"'})),
        ('"text/plain"; a=b', ('"text/plain"', {"a": "b"})),
        ("text/plain, text/html; a=b", ("text/plain, text/html", {"a": "b"})),
        ("not a media type", ("not a media type", {})),
        ("text/plain; x=\xe9\udcff\x00", ("text/plain", {"x": "\xe9\udcff\x00"})),
        ('text/plain; x="a\\\nb"', ("text/plain", {"x": "a\nb"})),
    ],
)
def test_malformed_values_do_not_raise(
    content_type: str, expected: tuple[str, dict[str, str]]
) -> None:
    assert parse_content_type(content_type) == expected


@pytest.mark.parametrize(
    "content_type",
    [
        '"',
        '""',
        '"\\',
        "\\",
        "=",
        "=;=",
        ';"=";',
        "\x00;\x00=\x00",
        ';"' * 1000,
        "\\" * 1001 + '"',
        ";" * 10000,
        "a=" * 10000,
    ],
)
def test_arbitrary_input_returns_strings(content_type: str) -> None:
    media_type, params = parse_content_type(content_type)

    assert isinstance(media_type, str)
    assert all(
        isinstance(name, str) and isinstance(value, str)
        for name, value in params.items()
    )
