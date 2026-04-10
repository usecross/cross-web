from flask import Flask
import pytest

from cross_web.testing.clients.flask import FlaskHttpClient

pytestmark = [pytest.mark.flask]


def test_build_request_kwargs_returns_raw_data_without_files() -> None:
    client = FlaskHttpClient(Flask(__name__))

    result = client._build_request_kwargs(
        data=b"payload",
        json_data=None,
        files=None,
        extra="value",
    )

    assert result == {"extra": "value", "data": b"payload"}


def test_build_request_kwargs_requires_mapping_for_files() -> None:
    client = FlaskHttpClient(Flask(__name__))

    with pytest.raises(TypeError, match="mapping form data"):
        client._build_request_kwargs(
            data="payload",
            json_data=None,
            files={"file": ("test.txt", b"body", None)},
        )
