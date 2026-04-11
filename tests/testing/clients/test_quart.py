import pytest

pytest.importorskip("quart")

from quart import Quart

from cross_web.testing.clients.quart import QuartHttpClient

pytestmark = [pytest.mark.quart]


def test_build_request_kwargs_requires_mapping_for_files() -> None:
    client = QuartHttpClient(Quart(__name__))

    with pytest.raises(TypeError, match="mapping form data"):
        client._build_request_kwargs(
            data="payload",
            json_data=None,
            files={"file": ("test.txt", b"body", None)},
        )


def test_build_request_kwargs_uses_form_for_mapping_data() -> None:
    client = QuartHttpClient(Quart(__name__))

    result = client._build_request_kwargs(
        data={"field": "value"},
        json_data=None,
        files=None,
        extra="value",
    )

    assert result == {"extra": "value", "form": {"field": "value"}}


def test_build_request_kwargs_uses_data_for_raw_bytes() -> None:
    client = QuartHttpClient(Quart(__name__))

    result = client._build_request_kwargs(
        data=b"payload",
        json_data=None,
        files=None,
        extra="value",
    )

    assert result == {"extra": "value", "data": b"payload"}
