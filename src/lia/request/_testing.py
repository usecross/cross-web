from __future__ import annotations

import json
from typing import Any, Mapping, Optional

from ._base import AsyncHTTPRequestAdapter, FormData, HTTPMethod, QueryParams


class TestingRequestAdapter(AsyncHTTPRequestAdapter):
    __test__ = False

    def __init__(
        self,
        *,
        method: HTTPMethod = "POST",
        query_params: QueryParams | None = None,
        headers: Mapping[str, str] | None = None,
        content_type: str | None = None,
        url: str = "http://testserver/",
        cookies: Mapping[str, str] | None = None,
        form_data: FormData | None = None,
        json: dict[str, Any] | None = None,
    ) -> None:
        self._method = method
        self._query_params = query_params or {}
        self._headers = headers or {}
        self._content_type = content_type
        self._url = url
        self._cookies = cookies or {}
        self._form_data = form_data or FormData(files={}, form={})
        self._json = json

    @property
    def method(self) -> HTTPMethod:
        return self._method

    @property
    def query_params(self) -> QueryParams:
        return self._query_params

    @property
    def headers(self) -> Mapping[str, str]:
        return self._headers

    @property
    def content_type(self) -> Optional[str]:
        return self._content_type

    async def get_body(self) -> bytes:
        if self._json is not None:
            return json.dumps(self._json).encode("utf-8")

        return b""

    async def get_form_data(self) -> FormData:
        return self._form_data

    @property
    def url(self) -> str:
        return self._url

    @property
    def cookies(self) -> Mapping[str, str]:
        return self._cookies
