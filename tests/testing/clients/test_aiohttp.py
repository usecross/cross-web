from aiohttp import web
import pytest

from cross_web.testing.clients.aiohttp import AiohttpHttpClient

pytestmark = [pytest.mark.aiohttp]


def test_build_data_returns_raw_data_without_files() -> None:
    client = AiohttpHttpClient(web.Application())

    assert client._build_data(b"payload", None) == b"payload"


def test_build_data_requires_mapping_for_multipart() -> None:
    client = AiohttpHttpClient(web.Application())

    with pytest.raises(TypeError, match="mapping form data"):
        client._build_data("payload", {"file": ("test.txt", b"body", None)})
