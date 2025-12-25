import json
import pytest

from cross_web import AsyncDjangoHTTPRequestAdapter, DjangoHTTPRequestAdapter

pytestmark = [pytest.mark.django]


@pytest.fixture(scope="module", autouse=True)
def django_setup() -> None:
    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY="test-secret-key",
            DEFAULT_CHARSET="utf-8",
            USE_TZ=True,
            ALLOWED_HOSTS=["*"],
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
            ],
            MIDDLEWARE=[],
            ROOT_URLCONF="tests.request.django_urls",
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
        )
        django.setup()


def test_sync_django_adapter() -> None:
    from django.test import RequestFactory
    from django.core.files.uploadedfile import SimpleUploadedFile

    factory = RequestFactory()

    # Create a POST request with form data and files
    request = factory.post(
        "/test?query=test",
        data={
            "form": "data",
            "file": SimpleUploadedFile(
                "test.txt", b"upload", content_type="text/plain"
            ),
        },
        HTTP_COOKIE="session=123",
    )

    adapter = DjangoHTTPRequestAdapter(request)

    assert adapter.query_params == {"query": "test"}
    # Django doesn't consume body for multipart, it's still available
    assert adapter.body  # Body contains multipart data
    assert adapter.method == "POST"
    assert "Content-Type" in adapter.headers
    assert adapter.headers["Content-Type"].startswith("multipart/form-data")
    assert adapter.post_data["form"] == "data"
    assert "file" in adapter.files
    assert adapter.content_type is not None and adapter.content_type.startswith(
        "multipart/form-data"
    )
    assert adapter.url == "http://testserver/test?query=test"
    assert adapter.cookies == {"session": "123"}

    form_data = adapter.get_form_data()
    assert "file" in form_data.files
    assert form_data.form["form"] == "data"


def test_sync_django_adapter_json() -> None:
    from django.test import RequestFactory

    factory = RequestFactory()

    # Create a POST request with JSON data
    request = factory.post(
        "/test?query=test",
        data=json.dumps({"key": "value"}),
        content_type="application/json",
        HTTP_COOKIE="session=123",
    )

    adapter = DjangoHTTPRequestAdapter(request)

    assert adapter.query_params == {"query": "test"}
    assert adapter.body == '{"key": "value"}'
    assert adapter.method == "POST"
    assert adapter.headers["Content-Type"] == "application/json"
    assert adapter.content_type == "application/json"
    assert adapter.url == "http://testserver/test?query=test"
    assert adapter.cookies == {"session": "123"}


@pytest.mark.asyncio
async def test_async_django_adapter() -> None:
    from django.test import RequestFactory
    from django.core.files.uploadedfile import SimpleUploadedFile

    factory = RequestFactory()

    # Create a POST request with form data and files
    request = factory.post(
        "/test?query=test",
        data={
            "form": "data",
            "file": SimpleUploadedFile(
                "test.txt", b"upload", content_type="text/plain"
            ),
        },
        HTTP_COOKIE="session=123",
    )

    adapter = AsyncDjangoHTTPRequestAdapter(request)

    assert adapter.query_params == {"query": "test"}
    body = await adapter.get_body()
    assert body  # Body contains multipart data
    assert adapter.method == "POST"
    assert "Content-Type" in adapter.headers
    assert adapter.content_type is not None and adapter.content_type.startswith(
        "multipart/form-data"
    )
    assert adapter.url == "http://testserver/test?query=test"
    assert adapter.cookies == {"session": "123"}

    form_data = await adapter.get_form_data()
    assert "file" in form_data.files
    assert form_data.form["form"] == "data"


@pytest.mark.asyncio
async def test_async_django_adapter_json() -> None:
    from django.test import RequestFactory

    factory = RequestFactory()

    # Create a POST request with JSON data
    request = factory.post(
        "/test?query=test",
        data=json.dumps({"key": "value"}),
        content_type="application/json",
        HTTP_COOKIE="session=123",
    )

    adapter = AsyncDjangoHTTPRequestAdapter(request)

    assert adapter.query_params == {"query": "test"}
    body = await adapter.get_body()
    assert body == b'{"key": "value"}'
    assert adapter.method == "POST"
    assert adapter.headers["Content-Type"] == "application/json"
    assert adapter.content_type == "application/json"
    assert adapter.url == "http://testserver/test?query=test"
    assert adapter.cookies == {"session": "123"}
