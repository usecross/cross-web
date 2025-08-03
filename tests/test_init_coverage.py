"""
Test __init__ lines that need coverage
"""

from unittest.mock import Mock
from lia import (
    DjangoHTTPRequestAdapter,
    AsyncDjangoHTTPRequestAdapter,
    FlaskHTTPRequestAdapter,
    AsyncFlaskHTTPRequestAdapter,
)


def test_django_sync_init() -> None:
    """Test Django sync adapter __init__ - line 14"""
    request = Mock()
    adapter = DjangoHTTPRequestAdapter(request)
    assert adapter.request == request


def test_django_async_init() -> None:
    """Test Django async adapter __init__"""
    request = Mock()

    adapter = AsyncDjangoHTTPRequestAdapter(request)
    assert adapter.request == request


def test_flask_sync_init() -> None:
    """Test Flask sync adapter __init__ - line 14"""
    request = Mock()
    adapter = FlaskHTTPRequestAdapter(request)
    assert adapter.request == request


def test_flask_async_init() -> None:
    """Test Flask async adapter __init__ - line 14"""
    request = Mock()
    adapter = AsyncFlaskHTTPRequestAdapter(request)
    assert adapter.request == request
