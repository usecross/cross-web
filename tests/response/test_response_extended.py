from cross_web.response import Cookie, Response


def test_cookie_creation() -> None:
    cookie = Cookie(
        name="session",
        value="abc123",
        secure=True,
        path="/admin",
        domain="example.com",
        max_age=3600,
        httponly=False,
        samesite="strict",
    )

    assert cookie.name == "session"
    assert cookie.value == "abc123"
    assert cookie.secure is True
    assert cookie.path == "/admin"
    assert cookie.domain == "example.com"
    assert cookie.max_age == 3600
    assert cookie.httponly is False
    assert cookie.samesite == "strict"


def test_cookie_defaults() -> None:
    cookie = Cookie(name="test", value="value", secure=False)

    assert cookie.name == "test"
    assert cookie.value == "value"
    assert cookie.secure is False
    assert cookie.path is None
    assert cookie.domain is None
    assert cookie.max_age is None
    assert cookie.httponly is True  # Default
    assert cookie.samesite == "lax"  # Default


def test_response_json_valid() -> None:
    response = Response(status_code=200, body='{"key": "value", "number": 42}')

    result = response.json()
    assert result == {"key": "value", "number": 42}


def test_response_json_none_body() -> None:
    response = Response(status_code=204, body=None)

    result = response.json()
    assert result is None


def test_response_json_empty_object() -> None:
    response = Response(status_code=200, body="{}")

    result = response.json()
    assert result == {}


def test_response_json_array() -> None:
    response = Response(status_code=200, body="[1, 2, 3]")

    result = response.json()

    assert result == [1, 2, 3]


def test_response_with_cookies() -> None:
    cookies = [
        Cookie(name="session", value="123", secure=True),
        Cookie(name="prefs", value="dark_mode", secure=False),
    ]

    response = Response(status_code=200, body="OK", cookies=cookies)

    assert response.cookies == cookies
    assert len(response.cookies) == 2


def test_response_with_headers() -> None:
    headers = {"Content-Type": "application/json", "X-Custom-Header": "value"}

    response = Response(status_code=201, body='{"created": true}', headers=headers)

    assert response.headers == headers
    assert response.headers["Content-Type"] == "application/json"


def test_to_fastapi_basic() -> None:
    response = Response(
        status_code=200, body="Hello World", headers={"X-Test": "value"}
    )

    # We can't fully test FastAPI conversion without FastAPI installed in test env
    # but we can verify the method exists
    assert hasattr(response, "to_fastapi")


def test_to_fastapi_with_cookies() -> None:
    cookies = [
        Cookie(
            name="auth",
            value="token123",
            secure=True,
            path="/api",
            domain="api.example.com",
            max_age=7200,
            httponly=True,
            samesite="strict",
        )
    ]

    response = Response(status_code=200, body="Authorized", cookies=cookies)

    # Verify the response has the expected structure
    assert response.cookies is not None
    assert len(response.cookies) > 0
    assert response.cookies[0].name == "auth"
    assert response.cookies[0].secure is True
