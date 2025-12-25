from cross_web import Response


def test_redirect() -> None:
    response = Response.redirect("https://example.com")
    assert response.status_code == 302
    assert response.headers is not None
    assert response.headers["Location"] == "https://example.com"


def test_redirect_with_query_params() -> None:
    response = Response.redirect("https://example.com", {"a": "1", "b": "2"})
    assert response.status_code == 302
    assert response.headers is not None
    assert response.headers["Location"] == "https://example.com?a=1&b=2"


def test_redirect_with_headers() -> None:
    response = Response.redirect("https://example.com", headers={"X-Test": "test"})
    assert response.status_code == 302
    assert response.headers is not None
    assert response.headers["Location"] == "https://example.com"
    assert response.headers["X-Test"] == "test"
