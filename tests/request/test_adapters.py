import io
import pytest
from urllib.parse import urlencode

from lia import (
    AiohttpHTTPRequestAdapter,
    AsyncDjangoHTTPRequestAdapter,
    AsyncFlaskHTTPRequestAdapter,
    ChaliceHTTPRequestAdapter,
    DjangoHTTPRequestAdapter,
    FlaskHTTPRequestAdapter,
    LitestarRequestAdapter,
    QuartHTTPRequestAdapter,
    SanicHTTPRequestAdapter,
    StarletteRequestAdapter,
)


class TestDjangoAdapters:
    def test_sync_django_adapter(self):
        from django.http import HttpRequest, QueryDict
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create real Django HttpRequest
        request = HttpRequest()
        request.method = "POST"
        request.META = {
            "HTTP_CONTENT_TYPE": "application/json",
            "HTTP_HOST": "example.com",
            "PATH_INFO": "/test",
            "wsgi.url_scheme": "http",
        }
        request.GET = QueryDict("query=test")
        request._body = b"test body"
        request.POST = QueryDict("form=data")
        request.FILES = {"file": SimpleUploadedFile("test.txt", b"upload")}
        request.COOKIES = {"session": "123"}
        
        adapter = DjangoHTTPRequestAdapter(request)
        
        assert adapter.query_params == {"query": "test"}
        assert adapter.body == "test body"
        assert adapter.method == "POST"
        assert "Content-Type" in adapter.headers
        assert adapter.headers["Content-Type"] == "application/json"
        assert adapter.post_data["form"] == "data"
        assert "file" in adapter.files
        assert adapter.content_type == "application/json"
        assert adapter.url == "http://example.com/test"
        assert adapter.cookies == {"session": "123"}
        
        form_data = adapter.get_form_data()
        assert "file" in form_data["files"]
        assert form_data["form"]["form"] == "data"
    
    @pytest.mark.asyncio
    async def test_async_django_adapter(self):
        from django.http import HttpRequest, QueryDict
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create real Django HttpRequest
        request = HttpRequest()
        request.method = "POST"
        request.META = {
            "HTTP_CONTENT_TYPE": "application/json",
            "HTTP_HOST": "example.com",
            "PATH_INFO": "/test",
            "wsgi.url_scheme": "http",
        }
        request.GET = QueryDict("query=test")
        request._body = b"test body"
        request.POST = QueryDict("form=data")
        request.FILES = {"file": SimpleUploadedFile("test.txt", b"upload")}
        request.COOKIES = {"session": "123"}
        
        adapter = AsyncDjangoHTTPRequestAdapter(request)
        
        assert adapter.query_params == {"query": "test"}
        assert await adapter.get_body() == b"test body"
        assert adapter.method == "POST"
        assert "Content-Type" in adapter.headers
        assert adapter.content_type == "application/json"
        assert adapter.url == "http://example.com/test"
        assert adapter.cookies == {"session": "123"}
        
        form_data = await adapter.get_form_data()
        assert "file" in form_data["files"]
        assert form_data["form"]["form"] == "data"


class TestFlaskAdapters:
    def test_sync_flask_adapter(self):
        from flask import Flask, Request
        from werkzeug.datastructures import FileStorage, ImmutableMultiDict
        
        app = Flask(__name__)
        
        with app.test_request_context(
            "/test?query=test",
            method="POST",
            data=b"test body",
            headers={"Content-Type": "application/json"},
        ):
            # Create a request with form data and files
            request = Request.from_values(
                path="/test",
                query_string="query=test",
                method="POST",
                data={"form": "data"},
                files={"file": FileStorage(stream=io.BytesIO(b"upload"), filename="test.txt")},
                headers={"Content-Type": "application/json"},
                environ_base={"HTTP_COOKIE": "session=123"},
            )
            
            adapter = FlaskHTTPRequestAdapter(request)
            
            assert adapter.query_params == {"query": "test"}
            assert adapter.method == "POST"
            assert adapter.headers["Content-Type"] == "application/json"
            assert adapter.post_data["form"] == "data"
            assert "file" in adapter.files
            assert adapter.content_type == "application/x-www-form-urlencoded"
            assert "/test" in adapter.url
            assert adapter.cookies == {"session": "123"}
            
            form_data = adapter.get_form_data()
            assert "file" in form_data["files"]
            assert form_data["form"]["form"] == "data"
    
    @pytest.mark.asyncio
    async def test_async_flask_adapter(self):
        from flask import Flask, Request
        from werkzeug.datastructures import FileStorage
        
        app = Flask(__name__)
        
        with app.test_request_context():
            request = Request.from_values(
                path="/test",
                query_string="query=test",
                method="POST",
                data=b"test body",
                files={"file": FileStorage(stream=io.BytesIO(b"upload"), filename="test.txt")},
                headers={"Content-Type": "application/json"},
                environ_base={"HTTP_COOKIE": "session=123"},
            )
            
            adapter = AsyncFlaskHTTPRequestAdapter(request)
            
            assert adapter.query_params == {"query": "test"}
            assert await adapter.get_body() == b"test body"
            assert adapter.method == "POST"
            assert adapter.headers["Content-Type"] == "application/json"
            assert adapter.content_type == "application/json"
            assert "/test" in adapter.url
            assert adapter.cookies == {"session": "123"}
            
            form_data = await adapter.get_form_data()
            assert "file" in form_data["files"]


class TestSanicAdapter:
    @pytest.mark.asyncio
    async def test_sanic_adapter(self):
        from sanic import Sanic
        from sanic.request import Request, File
        
        app = Sanic("test")
        
        # Create a Sanic request
        headers = {"content-type": "application/json"}
        request = Request(
            url_bytes=b"http://example.com/test?query=test",
            headers=headers,
            version="1.1",
            method="POST",
            transport=None,
            app=app,
        )
        request.body = b"test body"
        request._parsed_url = request.parse_url()
        request._form = {"form": "data"}
        request._files = {"textFile": [File(type="text/plain", body=b"upload", name="textFile.txt")]}
        request._cookies = {"session": "123"}
        
        adapter = SanicHTTPRequestAdapter(request)
        
        assert adapter.query_params == {"query": "test"}
        assert await adapter.get_body() == b"test body"
        assert adapter.method == "POST"
        assert adapter.headers["content-type"] == "application/json"
        assert adapter.content_type == "application/json"
        assert adapter.url == "http://example.com/test?query=test"
        assert adapter.cookies == {"session": "123"}
        
        form_data = await adapter.get_form_data()
        assert form_data["form"]["form"] == "data"
        assert "textFile" in form_data["files"]


class TestAiohttpAdapter:
    @pytest.mark.asyncio
    async def test_aiohttp_adapter(self):
        from aiohttp import web
        from aiohttp.test_utils import make_mocked_request
        from yarl import URL
        
        # Create a real aiohttp request
        request = make_mocked_request(
            "POST",
            "/test?query=test",
            headers={"content-type": "application/json"},
            payload=b"test body",
        )
        request._url = URL("http://example.com/test?query=test")
        request.cookies = {"session": "123"}
        
        adapter = AiohttpHTTPRequestAdapter(request)
        
        assert adapter.query_params == {"query": "test"}
        assert adapter.method == "POST"
        assert adapter.headers["content-type"] == "application/json"
        assert adapter.content_type == "application/json"
        assert str(adapter.url) == "http://example.com/test?query=test"
        assert adapter.cookies == {"session": "123"}


class TestQuartAdapter:
    @pytest.mark.asyncio
    async def test_quart_adapter(self):
        from quart import Quart
        from werkzeug.datastructures import FileStorage
        
        app = Quart(__name__)
        
        async with app.test_request_context(
            "/test?query=test",
            method="POST",
            data=b"test body",
            headers={"Content-Type": "application/json"},
        ) as ctx:
            request = ctx.request
            request._cookies = {"session": "123"}
            
            # Manually set form and files for testing
            request._form = {"form": "data"}
            request._files = {"file": FileStorage(stream=io.BytesIO(b"upload"), filename="test.txt")}
            
            adapter = QuartHTTPRequestAdapter(request)
            
            assert adapter.query_params == {"query": "test"}
            assert await adapter.get_body() == b"test body"
            assert adapter.method == "POST"
            assert adapter.headers["Content-Type"] == "application/json"
            assert adapter.content_type == "application/json"
            assert "test" in adapter.url
            assert adapter.cookies == {"session": "123"}


class TestChaliceAdapter:
    def test_chalice_adapter(self):
        from chalice.app import Request
        
        # Create a Chalice request
        event = {
            "httpMethod": "POST",
            "headers": {"Content-Type": "application/json"},
            "queryStringParameters": {"query": "test"},
            "body": "dGVzdCBib2R5",  # base64 encoded "test body"
            "isBase64Encoded": True,
            "requestContext": {
                "stage": "dev",
                "domainName": "api.example.com",
                "path": "/graphql",
            },
        }
        
        request = Request(event, context={})
        
        adapter = ChaliceHTTPRequestAdapter(request)
        
        assert adapter.query_params == {"query": "test"}
        assert adapter.body == b"test body"
        assert adapter.method == "POST"
        assert adapter.headers["Content-Type"] == "application/json"
        assert adapter.content_type == "application/json"
        assert adapter.url == "https://api.example.com/dev/graphql?query=test"
        
        # Test cookie parsing
        event["headers"]["Cookie"] = "session=123; user=john"
        request = Request(event, context={})
        adapter = ChaliceHTTPRequestAdapter(request)
        assert adapter.cookies == {"session": "123", "user": "john"}
        
        # Test NotImplementedError for form data
        with pytest.raises(NotImplementedError):
            adapter.post_data
        
        with pytest.raises(NotImplementedError):
            adapter.files
        
        with pytest.raises(NotImplementedError):
            adapter.get_form_data()


class TestLitestarAdapter:
    @pytest.mark.asyncio
    async def test_litestar_adapter(self):
        import httpx
        from litestar import Litestar, post, Request
        from litestar.datastructures import UploadFile
        from litestar.testing import create_test_client
        
        @post("/test")
        async def handler(request: Request) -> dict:
            adapter = LitestarRequestAdapter(request)
            
            # Store adapter for assertions
            handler.adapter = adapter
            
            return {"status": "ok"}
        
        app = Litestar([handler])
        
        with create_test_client(app) as client:
            response = client.post(
                "/test?query=test",
                content=b"test body",
                headers={"Content-Type": "application/json"},
                cookies={"session": "123"},
            )
            
            # Get the adapter from the handler
            adapter = handler.adapter
            
            assert adapter.query_params == {"query": "test"}
            assert adapter.method == "POST"
            assert adapter.headers["content-type"] == "application/json"
            assert adapter.content_type == "application/json"
            assert "test" in adapter.url
            assert adapter.cookies == {"session": "123"}


class TestStarletteAdapter:
    @pytest.mark.asyncio
    async def test_starlette_adapter(self):
        from starlette.applications import Starlette
        from starlette.requests import Request
        from starlette.responses import JSONResponse
        from starlette.routing import Route
        from starlette.testclient import TestClient
        
        async def handler(request: Request):
            adapter = StarletteRequestAdapter(request)
            
            # Store adapter for assertions
            handler.adapter = adapter
            
            return JSONResponse({"status": "ok"})
        
        app = Starlette(routes=[Route("/test", handler, methods=["POST"])])
        
        with TestClient(app) as client:
            response = client.post(
                "/test?query=test",
                content=b"test body",
                headers={"Content-Type": "application/json"},
                cookies={"session": "123"},
            )
            
            # Get the adapter from the handler
            adapter = handler.adapter
            
            assert adapter.query_params == {"query": "test"}
            assert adapter.method == "POST"
            assert adapter.headers["content-type"] == "application/json"
            assert adapter.content_type == "application/json"
            assert "test" in str(adapter.url)
            assert adapter.cookies == {"session": "123"}