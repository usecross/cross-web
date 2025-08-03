import pytest
from lia.request import AsyncHTTPRequest
from lia.request._base import FormData
from lia.request._testing import TestingRequestAdapter


def test_async_http_request_init():
    adapter = TestingRequestAdapter()
    request = AsyncHTTPRequest(adapter)
    assert request._adapter is adapter


@pytest.mark.asyncio
async def test_async_http_request_properties():
    adapter = TestingRequestAdapter(
        method="PUT",
        query_params={"q": "search"},
        headers={"Authorization": "Bearer token"},
        content_type="application/json",
        url="https://api.example.com/endpoint",
        cookies={"session_id": "xyz789"},
    )
    request = AsyncHTTPRequest(adapter)
    
    assert request.method == "PUT"
    assert request.query_params == {"q": "search"}
    assert request.headers == {"Authorization": "Bearer token"}
    assert request.content_type == "application/json"
    assert request.url == "https://api.example.com/endpoint"
    assert request.cookies == {"session_id": "xyz789"}


@pytest.mark.asyncio
async def test_async_http_request_get_body():
    adapter = TestingRequestAdapter(json={"data": "test"})
    request = AsyncHTTPRequest(adapter)
    
    body = await request.get_body()
    assert body == b'{"data": "test"}'


@pytest.mark.asyncio
async def test_async_http_request_get_form_data():
    form_data = FormData(
        files={"upload": "file_content"},
        form={"name": "test", "value": "123"}
    )
    adapter = TestingRequestAdapter(form_data=form_data)
    request = AsyncHTTPRequest(adapter)
    
    result = await request.get_form_data()
    assert result.files == {"upload": "file_content"}
    assert result.form == {"name": "test", "value": "123"}


def test_from_form_data():
    data = {"username": "john", "password": "secret"}
    request = AsyncHTTPRequest.from_form_data(data)
    
    assert request.method == "POST"
    assert request.content_type == "application/x-www-form-urlencoded"
    
    # Check form data was set correctly
    assert request._adapter._form_data.form == data
    assert request._adapter._form_data.files == {}


@pytest.mark.asyncio
async def test_from_form_data_get_form_data():
    data = {"field1": "value1", "field2": "value2"}
    request = AsyncHTTPRequest.from_form_data(data)
    
    form_data = await request.get_form_data()
    assert form_data.form == data
    assert form_data.files == {}


# Test framework-specific constructors
# These tests verify the methods exist and can be called
def test_from_starlette():
    # We can't test this without a real Starlette request
    # Just verify the method exists
    assert hasattr(AsyncHTTPRequest, 'from_starlette')


def test_from_fastapi():
    # FastAPI uses Starlette requests, so this should be the same
    assert hasattr(AsyncHTTPRequest, 'from_fastapi')


def test_from_django():
    assert hasattr(AsyncHTTPRequest, 'from_django')


def test_from_flask():
    assert hasattr(AsyncHTTPRequest, 'from_flask')


def test_from_sanic():
    assert hasattr(AsyncHTTPRequest, 'from_sanic')


def test_from_aiohttp():
    assert hasattr(AsyncHTTPRequest, 'from_aiohttp')


def test_from_quart():
    assert hasattr(AsyncHTTPRequest, 'from_quart')


def test_from_litestar():
    assert hasattr(AsyncHTTPRequest, 'from_litestar')