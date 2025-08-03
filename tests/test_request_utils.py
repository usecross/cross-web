import pytest
from lia.request_utils import is_request_allowed, parse_query_params, should_render_ide


class MockRequest:
    def __init__(self, method="GET", query_params=None, headers=None):
        self.method = method
        self.query_params = query_params or {}
        self.headers = headers or {}


def test_is_request_allowed_default_methods():
    request = MockRequest(method="GET")
    assert is_request_allowed(request) is True

    request = MockRequest(method="POST")
    assert is_request_allowed(request) is True

    request = MockRequest(method="PUT")
    assert is_request_allowed(request) is False

    request = MockRequest(method="DELETE")
    assert is_request_allowed(request) is False


def test_is_request_allowed_custom_methods():
    request = MockRequest(method="PUT")
    assert is_request_allowed(request, allowed_methods=("PUT", "DELETE")) is True

    request = MockRequest(method="DELETE")
    assert is_request_allowed(request, allowed_methods=("PUT", "DELETE")) is True

    request = MockRequest(method="GET")
    assert is_request_allowed(request, allowed_methods=("PUT", "DELETE")) is False


def test_should_render_ide_get_request():
    request = MockRequest(method="GET", headers={"accept": "text/html"})
    assert should_render_ide(request) is True

    request = MockRequest(method="GET", headers={"accept": "*/*"})
    assert should_render_ide(request) is True

    request = MockRequest(method="GET", headers={"accept": "application/json"})
    assert should_render_ide(request) is False


def test_should_render_ide_non_get_request():
    request = MockRequest(method="POST", headers={"accept": "text/html"})
    assert should_render_ide(request) is False

    request = MockRequest(method="PUT", headers={"accept": "text/html"})
    assert should_render_ide(request) is False


def test_should_render_ide_with_query_param():
    request = MockRequest(
        method="GET", query_params={"query": "value"}, headers={"accept": "text/html"}
    )
    assert should_render_ide(request) is False

    request = MockRequest(
        method="GET", query_params={}, headers={"accept": "text/html"}
    )
    assert should_render_ide(request) is True

    request = MockRequest(
        method="GET",
        query_params={"other": "value"},
        headers={"accept": "text/html"},
    )
    assert should_render_ide(request) is True


def test_should_render_ide_custom_query_param():
    request = MockRequest(
        method="GET",
        query_params={"custom": "value"},
        headers={"accept": "text/html"},
    )
    assert should_render_ide(request, check_query_param="custom") is False

    request = MockRequest(
        method="GET", query_params={"query": "value"}, headers={"accept": "text/html"}
    )
    assert should_render_ide(request, check_query_param="custom") is True


def test_should_render_ide_custom_headers():
    request = MockRequest(method="GET", headers={"accept": "application/xml"})
    assert (
        should_render_ide(request, supported_headers=("application/xml", "text/xml"))
        is True
    )

    request = MockRequest(method="GET", headers={"accept": "application/json"})
    assert (
        should_render_ide(request, supported_headers=("application/xml", "text/xml"))
        is False
    )


def test_parse_query_params_no_json_fields():
    params = {"key": "value", "number": "123"}
    result = parse_query_params(params)
    assert result == {"key": "value", "number": "123"}


def test_parse_query_params_with_json_fields():
    params = {
        "variables": '{"id": 123, "name": "test"}',
        "extensions": '{"debug": true}',
        "normal": "value",
    }
    result = parse_query_params(params)
    assert result == {
        "variables": {"id": 123, "name": "test"},
        "extensions": {"debug": True},
        "normal": "value",
    }


def test_parse_query_params_empty_json_fields():
    params = {"variables": "", "extensions": None, "normal": "value"}
    result = parse_query_params(params)
    assert result == {"variables": "", "extensions": None, "normal": "value"}


def test_parse_query_params_custom_json_fields():
    params = {
        "custom_json": '{"test": true}',
        "variables": '{"id": 123}',
        "normal": "value",
    }
    result = parse_query_params(params, json_fields=("custom_json",))
    assert result == {
        "custom_json": {"test": True},
        "variables": '{"id": 123}',  # Not parsed because not in json_fields
        "normal": "value",
    }


def test_parse_query_params_missing_json_fields():
    params = {"normal": "value"}
    result = parse_query_params(params)
    assert result == {"normal": "value"}