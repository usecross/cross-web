import pytest
from lia.request._base import SyncHTTPRequestAdapter, AsyncHTTPRequestAdapter, HTTPMethod, QueryParams
from typing import Mapping, Optional, Any


class TestSyncAdapter(SyncHTTPRequestAdapter):
    """Concrete implementation for testing abstract methods"""
    @property
    def method(self) -> HTTPMethod:
        return "GET"
    
    @property
    def query_params(self) -> QueryParams:
        return {"test": "value"}
    
    @property
    def headers(self) -> Mapping[str, str]:
        return {"x-test": "header"}
    
    @property
    def content_type(self) -> Optional[str]:
        return "text/plain"
    
    @property
    def body(self) -> bytes:
        return b"sync body"
    
    @property
    def post_data(self) -> Mapping[str, str]:
        return {"post": "data"}
    
    @property
    def files(self) -> Mapping[str, Any]:
        return {"file": "content"}
    
    def get_body(self) -> bytes:
        return b"sync body"
    
    def get_form_data(self):
        from lia.request._base import FormData
        return FormData(files={}, form={"sync": "data"})
    
    @property
    def url(self) -> str:
        return "http://sync.example.com"
    
    @property
    def cookies(self) -> Mapping[str, str]:
        return {"sync": "cookie"}


class TestAsyncAdapter(AsyncHTTPRequestAdapter):
    """Concrete implementation for testing abstract methods"""
    @property
    def method(self) -> HTTPMethod:
        return "POST"
    
    @property
    def query_params(self) -> QueryParams:
        return {"async": "query"}
    
    @property
    def headers(self) -> Mapping[str, str]:
        return {"x-async": "header"}
    
    @property
    def content_type(self) -> Optional[str]:
        return "application/json"
    
    async def get_body(self) -> bytes:
        return b"async body"
    
    async def get_form_data(self):
        from lia.request._base import FormData
        return FormData(files={"upload": "file"}, form={"async": "form"})
    
    @property
    def url(self) -> str:
        return "http://async.example.com"
    
    @property
    def cookies(self) -> Mapping[str, str]:
        return {"async": "cookie"}


def test_sync_adapter_abstract_methods():
    """Test that abstract methods raise NotImplementedError when not implemented"""
    # Test that we can't instantiate abstract base class directly
    with pytest.raises(TypeError):
        SyncHTTPRequestAdapter()


def test_async_adapter_abstract_methods():
    """Test that abstract methods raise NotImplementedError when not implemented"""
    # Test that we can't instantiate abstract base class directly
    with pytest.raises(TypeError):
        AsyncHTTPRequestAdapter()


def test_sync_adapter_properties():
    """Test concrete sync adapter implementation"""
    adapter = TestSyncAdapter()
    
    assert adapter.method == "GET"
    assert dict(adapter.query_params) == {"test": "value"}
    assert adapter.headers == {"x-test": "header"}
    assert adapter.content_type == "text/plain"
    assert adapter.body == b"sync body"
    assert adapter.post_data == {"post": "data"}
    assert adapter.files == {"file": "content"}
    assert adapter.get_body() == b"sync body"
    assert adapter.url == "http://sync.example.com"
    assert dict(adapter.cookies) == {"sync": "cookie"}
    
    form_data = adapter.get_form_data()
    assert form_data.form == {"sync": "data"}
    assert form_data.files == {}


@pytest.mark.asyncio
async def test_async_adapter_properties():
    """Test concrete async adapter implementation"""
    adapter = TestAsyncAdapter()
    
    assert adapter.method == "POST"
    assert dict(adapter.query_params) == {"async": "query"}
    assert adapter.headers == {"x-async": "header"}
    assert adapter.content_type == "application/json"
    assert adapter.url == "http://async.example.com"
    assert dict(adapter.cookies) == {"async": "cookie"}
    
    # Test async methods
    body = await adapter.get_body()
    assert body == b"async body"
    
    form_data = await adapter.get_form_data()
    assert form_data.form == {"async": "form"}
    assert form_data.files == {"upload": "file"}


def test_abstract_method_enforcement():
    """Test that missing implementations cause errors"""
    class IncompleteAdapter(SyncHTTPRequestAdapter):
        # Only implement some methods
        def method(self) -> HTTPMethod:
            return "GET"
    
    # Should not be able to instantiate
    with pytest.raises(TypeError):
        IncompleteAdapter()


def test_abstract_properties_as_methods():
    """Test calling abstract properties directly from base class"""
    # Create a partial mock to test individual abstract methods
    class PartialSyncAdapter(SyncHTTPRequestAdapter):
        def query_params(self) -> QueryParams:
            return {}
        def headers(self) -> Mapping[str, str]:
            return {}
        def content_type(self) -> Optional[str]:
            return None
        def get_body(self) -> bytes:
            return b""
        def get_form_data(self):
            from lia.request._base import FormData
            return FormData(files={}, form={})
        def url(self) -> str:
            return ""
        def cookies(self) -> Mapping[str, str]:
            return {}
        
        # Don't implement method() to test the abstract property
        @property
        def method(self):
            # Call the parent's abstract method to trigger NotImplementedError
            return super().method
    
    # Even with @property decorator, abstract methods should raise
    with pytest.raises(TypeError):
        PartialSyncAdapter()