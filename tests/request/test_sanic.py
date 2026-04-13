from __future__ import annotations

import pytest

from cross_web.request._sanic import SanicHTTPRequestAdapter


class SanicRequestStub:
    def __init__(self) -> None:
        self.form = {"field": "value"}
        self.files = None


@pytest.mark.asyncio
async def test_sanic_adapter_get_form_data_without_files() -> None:
    adapter = SanicHTTPRequestAdapter(SanicRequestStub())

    form_data = await adapter.get_form_data()

    assert form_data.form == {"field": "value"}
    assert form_data.files == {}
