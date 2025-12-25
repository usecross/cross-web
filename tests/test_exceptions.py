import pytest
from cross_web.exceptions import HTTPException


def test_http_exception_initialization() -> None:
    exc = HTTPException(404, "Not Found")
    assert exc.status_code == 404
    assert exc.reason == "Not Found"
    assert str(exc) == "Not Found"


def test_http_exception_different_status_codes() -> None:
    exc = HTTPException(400, "Bad Request")
    assert exc.status_code == 400
    assert exc.reason == "Bad Request"

    exc = HTTPException(500, "Internal Server Error")
    assert exc.status_code == 500
    assert exc.reason == "Internal Server Error"


def test_http_exception_inheritance() -> None:
    exc = HTTPException(403, "Forbidden")
    assert isinstance(exc, Exception)

    # Test that it can be raised and caught
    with pytest.raises(HTTPException) as exc_info:
        raise HTTPException(401, "Unauthorized")

    assert exc_info.value.status_code == 401
    assert exc_info.value.reason == "Unauthorized"


def test_http_exception_as_base_exception() -> None:
    # Test that it can be caught as a regular Exception
    with pytest.raises(Exception) as exc_info:
        raise HTTPException(503, "Service Unavailable")

    assert isinstance(exc_info.value, HTTPException)
    assert exc_info.value.status_code == 503
