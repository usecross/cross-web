import pytest

from lia import ChaliceHTTPRequestAdapter

pytestmark = [pytest.mark.chalice]


def test_chalice_adapter():
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
    event["headers"]["Cookie"] = "session=123; user=john"
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


def test_chalice_adapter_non_base64():
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
