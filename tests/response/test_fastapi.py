import pytest

from cross_web import Response

pytestmark = [pytest.mark.fastapi]


def test_basic_response() -> None:
    from fastapi import Response as FastAPIResponse

    response = Response(
        body="Hello, world!",
        status_code=200,
        headers={"Content-Type": "text/plain"},
    )

    fastapi_response = response.to_fastapi()

    assert isinstance(fastapi_response, FastAPIResponse)

    assert fastapi_response.status_code == 200
    assert fastapi_response.headers["Content-Type"] == "text/plain"
    assert fastapi_response.body == b"Hello, world!"


def test_redirect() -> None:
    from fastapi import Response as FastAPIResponse

    response = Response.redirect("https://example.com")
    fastapi_response = response.to_fastapi()

    assert isinstance(fastapi_response, FastAPIResponse)

    assert fastapi_response.status_code == 302
    assert fastapi_response.headers["Location"] == "https://example.com"
