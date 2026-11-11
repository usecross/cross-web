from __future__ import annotations

from unittest.mock import Mock

from cross_web import HTTPRequest, TestingHTTPRequestAdapter


def test_http_request_properties() -> None:
    adapter = TestingHTTPRequestAdapter(
        method="PUT",
        query_params={"q": "search"},
        path_params={"user_id": "123"},
        headers={"Authorization": "Bearer token"},
        content_type="application/json",
        body='{"ok": true}',
        post_data={"name": "test"},
        files={"upload": "file_content"},
        url="https://api.example.com/endpoint",
        cookies={"session_id": "xyz789"},
        client_host="203.0.113.7",
    )
    request = HTTPRequest(adapter)

    assert request._adapter is adapter
    assert request.method == "PUT"
    assert request.query_params == {"q": "search"}
    assert request.path_params == {"user_id": "123"}
    assert request.headers == {"Authorization": "Bearer token"}
    assert request.content_type == "application/json"
    assert request.body == '{"ok": true}'
    assert request.post_data == {"name": "test"}
    assert request.files == {"upload": "file_content"}
    assert request.url == "https://api.example.com/endpoint"
    assert request.cookies == {"session_id": "xyz789"}
    assert request.client_host == "203.0.113.7"


def test_http_request_client_host_defaults_to_none() -> None:
    assert HTTPRequest(TestingHTTPRequestAdapter()).client_host is None


def test_http_request_body_and_form_properties() -> None:
    request = HTTPRequest(
        TestingHTTPRequestAdapter(
            body=b'{"ok": true}',
            post_data={"name": "test", "value": "123"},
            files={"upload": "file_content"},
        )
    )

    assert request.body == b'{"ok": true}'
    assert request.post_data == {"name": "test", "value": "123"}
    assert request.files == {"upload": "file_content"}


def test_from_form_data() -> None:
    data = {"username": "john", "password": "secret"}

    request = HTTPRequest.from_form_data(data)

    assert request.method == "POST"
    assert request.content_type == "application/x-www-form-urlencoded"
    assert request.body == ""
    assert request.post_data == data
    assert request.files == {}


def test_testing_http_request_adapter() -> None:
    adapter = TestingHTTPRequestAdapter(
        method="GET",
        query_params={"q": "search"},
        path_params={"user_id": "123"},
        headers={"X-Custom": "header"},
        content_type="text/plain",
        body="raw body",
        post_data={"field": "value"},
        files={"upload": "file_content"},
        url="https://example.com/test",
        cookies={"session": "abc123"},
    )
    request = HTTPRequest(adapter)

    assert request.method == "GET"
    assert request.query_params == {"q": "search"}
    assert request.path_params == {"user_id": "123"}
    assert request.headers == {"X-Custom": "header"}
    assert request.content_type == "text/plain"
    assert request.body == "raw body"
    assert request.post_data == {"field": "value"}
    assert request.files == {"upload": "file_content"}
    assert request.url == "https://example.com/test"
    assert request.cookies == {"session": "abc123"}


def test_from_django() -> None:
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.GET.dict.return_value = {"q": "search"}
    mock_request.resolver_match = Mock()
    mock_request.resolver_match.kwargs = {"item_id": "123"}
    mock_request.body = b""
    mock_request.headers = {"X-Test": "value"}
    mock_request.content_type = "application/json"
    mock_request.build_absolute_uri.return_value = (
        "https://example.com/items/123/?q=search"
    )
    mock_request.COOKIES = {"session": "abc123"}

    request = HTTPRequest.from_django(mock_request)

    assert isinstance(request, HTTPRequest)
    assert request._adapter.__class__.__name__ == "DjangoHTTPRequestAdapter"
    assert request.method == "GET"
    assert request.url == "https://example.com/items/123/?q=search"
    assert request.query_params == {"q": "search"}
    assert request.path_params == {"item_id": "123"}
    assert request.headers["X-Test"] == "value"
    assert request.content_type == "application/json"
    assert request.cookies == {"session": "abc123"}


def test_from_flask() -> None:
    mock_request = Mock()
    mock_request.method = "POST"
    mock_request.args.to_dict.return_value = {"q": "search"}
    mock_request.view_args = {"item_id": "123"}
    mock_request.data = b""
    mock_request.headers = {"X-Test": "value"}
    mock_request.form = {"field": "value"}
    mock_request.files = {"upload": "file_content"}
    mock_request.content_type = "application/x-www-form-urlencoded"
    mock_request.url = "https://example.com/items/123/?q=search"
    mock_request.cookies = {"session": "abc123"}

    request = HTTPRequest.from_flask(mock_request)

    assert isinstance(request, HTTPRequest)
    assert request._adapter.__class__.__name__ == "FlaskHTTPRequestAdapter"
    assert request.method == "POST"
    assert request.url == "https://example.com/items/123/?q=search"
    assert request.query_params == {"q": "search"}
    assert request.path_params == {"item_id": "123"}
    assert request.headers["X-Test"] == "value"
    assert request.content_type == "application/x-www-form-urlencoded"
    assert request.post_data == {"field": "value"}
    assert request.files == {"upload": "file_content"}
    assert request.cookies == {"session": "abc123"}


def test_from_chalice() -> None:
    mock_request = Mock()
    mock_request.method = "GET"
    mock_request.query_params = {"q": "search"}
    mock_request.uri_params = {"item_id": "123"}
    mock_request.raw_body = b""
    mock_request.headers = {
        "Content-Type": "application/json",
        "Cookie": "session=abc123; theme=light",
        "X-Test": "value",
    }
    mock_request.context = {
        "domainName": "example.com",
        "path": "/items/123",
        "stage": "dev",
    }

    request = HTTPRequest.from_chalice(mock_request)

    assert isinstance(request, HTTPRequest)
    assert request._adapter.__class__.__name__ == "ChaliceHTTPRequestAdapter"
    assert request.method == "GET"
    assert request.url == "https://example.com/dev/items/123?q=search"
    assert request.query_params == {"q": "search"}
    assert request.path_params == {"item_id": "123"}
    assert request.headers["X-Test"] == "value"
    assert request.content_type == "application/json"
    assert request.cookies == {"session": "abc123", "theme": "light"}
