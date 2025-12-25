import pytest

from cross_web import ChaliceHTTPRequestAdapter

pytestmark = [pytest.mark.chalice]


def test_chalice_adapter() -> None:
    from chalice.app import Request

    # Create a Chalice request
    event = {
        "headers": {"Content-Type": "application/json"},
        "multiValueQueryStringParameters": {"query": ["test"]},
        "pathParameters": None,
        "stageVariables": None,
        "body": "dGVzdCBib2R5",  # base64 encoded "test body"
        "isBase64Encoded": True,
        "requestContext": {
            "httpMethod": "POST",
            "stage": "dev",
            "domainName": "api.example.com",
            "path": "/graphql",
            "resourcePath": "/graphql",
        },
    }

    request = Request(event)

    adapter = ChaliceHTTPRequestAdapter(request)

    assert adapter.query_params == {"query": "test"}
    assert adapter.body == b"test body"
    assert adapter.method == "POST"
    assert adapter.headers["Content-Type"] == "application/json"
    assert adapter.content_type == "application/json"
    assert adapter.url == "https://api.example.com/dev/graphql?query=test"

    # Test cookie parsing
    event["headers"]["Cookie"] = "session=123; user=john"  # type: ignore[index]
    request = Request(event)
    adapter = ChaliceHTTPRequestAdapter(request)
    assert adapter.cookies == {"session": "123", "user": "john"}

    # Test NotImplementedError for form data
    with pytest.raises(NotImplementedError):
        adapter.post_data

    with pytest.raises(NotImplementedError):
        adapter.files

    with pytest.raises(NotImplementedError):
        adapter.get_form_data()


def test_chalice_adapter_non_base64() -> None:
    from chalice.app import Request

    # Create a Chalice request with non-base64 body
    event = {
        "headers": {"Content-Type": "application/json"},
        "multiValueQueryStringParameters": {"query": ["test"]},
        "pathParameters": None,
        "stageVariables": None,
        "body": '{"key": "value"}',
        "isBase64Encoded": False,
        "requestContext": {
            "httpMethod": "POST",
            "stage": "dev",
            "domainName": "api.example.com",
            "path": "/graphql",
            "resourcePath": "/graphql",
        },
    }

    request = Request(event)

    adapter = ChaliceHTTPRequestAdapter(request)

    assert adapter.query_params == {"query": "test"}
    assert adapter.body == b'{"key": "value"}'
    assert adapter.method == "POST"
    assert adapter.headers["Content-Type"] == "application/json"
    assert adapter.content_type == "application/json"
    assert adapter.url == "https://api.example.com/dev/graphql?query=test"


def test_chalice_adapter_prod_stage() -> None:
    """Test Chalice adapter with prod stage - line 62"""
    from chalice.app import Request

    event = {
        "headers": {},
        "multiValueQueryStringParameters": {},
        "pathParameters": None,
        "stageVariables": None,
        "body": "",
        "isBase64Encoded": False,
        "requestContext": {
            "httpMethod": "GET",
            "stage": "prod",  # This triggers line 62
            "domainName": "api.example.com",
            "path": "/test",
            "resourcePath": "/test",
        },
    }

    request = Request(event)
    adapter = ChaliceHTTPRequestAdapter(request)

    # URL should not include /prod
    assert adapter.url == "https://api.example.com/test"


def test_chalice_adapter_no_stage() -> None:
    """Test Chalice adapter with no stage - line 62"""
    from chalice.app import Request

    event = {
        "headers": {},
        "multiValueQueryStringParameters": {},
        "pathParameters": None,
        "stageVariables": None,
        "body": "",
        "isBase64Encoded": False,
        "requestContext": {
            "httpMethod": "GET",
            "stage": "",  # Empty stage also triggers line 62
            "domainName": "api.example.com",
            "path": "/test",
            "resourcePath": "/test",
        },
    }

    request = Request(event)
    adapter = ChaliceHTTPRequestAdapter(request)

    # URL should not include stage
    assert adapter.url == "https://api.example.com/test"


def test_chalice_adapter_no_cookies() -> None:
    """Test Chalice adapter with no cookies - line 79"""
    from chalice.app import Request

    event = {
        "headers": {},  # No Cookie header
        "multiValueQueryStringParameters": {},
        "pathParameters": None,
        "stageVariables": None,
        "body": "",
        "isBase64Encoded": False,
        "requestContext": {
            "httpMethod": "GET",
            "stage": "dev",
            "domainName": "api.example.com",
            "path": "/test",
            "resourcePath": "/test",
        },
    }

    request = Request(event)
    adapter = ChaliceHTTPRequestAdapter(request)

    # Should return empty dict when no Cookie header - line 79
    assert adapter.cookies == {}
