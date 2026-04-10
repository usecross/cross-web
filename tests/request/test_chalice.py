import pytest

from cross_web import ChaliceHTTPRequestAdapter

pytestmark = [pytest.mark.chalice]


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


def test_chalice_adapter_non_prod_stage() -> None:
    """Test Chalice adapter with non-prod stage - line 60"""
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
            "stage": "dev",
            "domainName": "api.example.com",
            "path": "/test",
            "resourcePath": "/test",
        },
    }

    request = Request(event)
    adapter = ChaliceHTTPRequestAdapter(request)

    assert adapter.url == "https://api.example.com/dev/test"


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
