"""
Test specific Sanic adapter lines for coverage
"""

from unittest.mock import Mock


def test_sanic_process_files_none() -> None:
    """Test Sanic process_files with None files - line 29"""
    from cross_web.request._sanic import convert_request_to_files_dict

    # Mock request with None files
    request = Mock()
    request.files = None

    # This should trigger line 29 - return {}
    result = convert_request_to_files_dict(request)
    assert result == {}


def test_sanic_process_files_empty() -> None:
    """Test Sanic process_files with empty files - line 29"""
    from cross_web.request._sanic import convert_request_to_files_dict

    # Mock request with empty files dict
    request = Mock()
    request.files = {}

    # This should also trigger line 29 - return {}
    result = convert_request_to_files_dict(request)
    assert result == {}
