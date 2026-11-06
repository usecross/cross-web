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


def test_redirect_merges_query_params_into_an_existing_query() -> None:
    response = Response.redirect("https://example.com/cb?a=1", {"code": "xyz"})
    assert response.headers is not None
    assert response.headers["Location"] == "https://example.com/cb?a=1&code=xyz"


def test_redirect_with_query_params_on_a_relative_url() -> None:
    response = Response.redirect("/next?tab=1", {"error": "access denied"})
    assert response.headers is not None
    assert response.headers["Location"] == "/next?tab=1&error=access+denied"


def test_redirect_keeps_the_fragment_after_the_query() -> None:
    response = Response.redirect("https://example.com/cb#top", {"a": "1"})
    assert response.headers is not None
    assert response.headers["Location"] == "https://example.com/cb?a=1#top"


def test_redirect_keeps_an_empty_fragment() -> None:
    # An explicit empty fragment stops the browser from carrying the original
    # URL's fragment over to the destination.
    response = Response.redirect("https://example.com/cb#", {"a": "1"})
    assert response.headers is not None
    assert response.headers["Location"] == "https://example.com/cb?a=1#"


def test_redirect_adds_no_separator_for_empty_query_params() -> None:
    response = Response.redirect("https://example.com/cb?a=1", {"b": []})
    assert response.headers is not None
    assert response.headers["Location"] == "https://example.com/cb?a=1"


def test_redirect_repeats_list_query_params() -> None:
    response = Response.redirect("https://example.com", {"scope": ["a", "b"]})
    assert response.headers is not None
    assert response.headers["Location"] == "https://example.com?scope=a&scope=b"


def test_redirect_with_headers() -> None:
    response = Response.redirect("https://example.com", headers={"X-Test": "test"})
    assert response.status_code == 302
    assert response.headers is not None
    assert response.headers["Location"] == "https://example.com"
    assert response.headers["X-Test"] == "test"
