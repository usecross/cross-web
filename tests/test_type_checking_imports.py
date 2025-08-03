"""
Test TYPE_CHECKING imports are covered
"""

# These imports trigger the TYPE_CHECKING blocks
import lia.request._starlette
import lia.request._quart
import lia.request._litestar
import lia.request._aiohttp
import lia.request._sanic
import lia.request._chalice
import lia.request
import lia.response


def test_modules_imported() -> None:
    """Verify modules are imported"""
    assert lia.request._starlette is not None
    assert lia.request._quart is not None
    assert lia.request._litestar is not None
    assert lia.request._aiohttp is not None
    assert lia.request._sanic is not None
    assert lia.request._chalice is not None
    assert lia.request is not None
    assert lia.response is not None
