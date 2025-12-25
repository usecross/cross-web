import pytest
from unittest.mock import Mock, AsyncMock
from cross_web import LitestarRequestAdapter


@pytest.mark.asyncio
async def test_litestar_adapter_get_body() -> None:
    """Test get_body method"""
    mock_request = Mock()
    mock_request.body = AsyncMock(return_value=b"litestar body content")

    adapter = LitestarRequestAdapter(mock_request)

    body = await adapter.get_body()
    assert body == b"litestar body content"
    mock_request.body.assert_called_once()


@pytest.mark.asyncio
async def test_litestar_adapter_get_form_data() -> None:
    """Test get_form_data method"""
    mock_request = Mock()

    # Mock form data
    mock_form_data = {"field1": "value1", "file1": "file_content"}
    mock_request.form = AsyncMock(return_value=mock_form_data)

    adapter = LitestarRequestAdapter(mock_request)

    form_data = await adapter.get_form_data()
    assert form_data.form == mock_form_data
    assert form_data.files == mock_form_data  # In Litestar, both point to same data
    mock_request.form.assert_called_once()


@pytest.mark.asyncio
async def test_litestar_adapter_content_type_with_params() -> None:
    """Test content_type with parameters"""
    mock_request = Mock()
    mock_request.content_type = (
        "multipart/form-data",
        {"boundary": "----WebKitFormBoundary", "charset": "utf-8"},
    )

    adapter = LitestarRequestAdapter(mock_request)

    content_type = adapter.content_type
    assert (
        content_type
        == "multipart/form-data; boundary=----WebKitFormBoundary; charset=utf-8"
    )


@pytest.mark.asyncio
async def test_litestar_adapter_content_type_no_params() -> None:
    """Test content_type without parameters"""
    mock_request = Mock()
    mock_request.content_type = ("application/json", {})

    adapter = LitestarRequestAdapter(mock_request)

    content_type = adapter.content_type
    assert content_type == "application/json"


@pytest.mark.asyncio
async def test_litestar_adapter_empty_form() -> None:
    """Test get_form_data with empty form"""
    mock_request = Mock()
    mock_request.form = AsyncMock(return_value={})

    adapter = LitestarRequestAdapter(mock_request)

    form_data = await adapter.get_form_data()
    assert form_data.form == {}
    assert form_data.files == {}
