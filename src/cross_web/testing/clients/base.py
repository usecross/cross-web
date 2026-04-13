from __future__ import annotations

import abc
import json
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Literal, Optional, Union, cast

JSON = Union[dict[str, "JSON"], list["JSON"], str, int, float, bool, None]
RequestData = Union[bytes, str, Mapping[str, object]]
UploadedFile = tuple[str, bytes, Optional[str]]
RequestMethod = Literal["head", "get", "post", "patch", "put", "delete"]


@dataclass
class Response:
    status_code: int
    data: bytes

    def __init__(
        self, status_code: int, data: bytes, *, headers: dict[str, str] | None = None
    ) -> None:
        self.status_code = status_code
        self.data = data
        self._headers = headers or {}

    @cached_property
    def headers(self) -> Mapping[str, str]:
        return {key.lower(): value for key, value in self._headers.items()}

    @property
    def text(self) -> str:
        return self.data.decode()

    @property
    def json(self) -> JSON:
        return cast(JSON, json.loads(self.data))


class HttpClient(abc.ABC):
    supports_form_data = True

    @abc.abstractmethod
    def __init__(self, app: Any) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def request(
        self,
        url: str,
        method: RequestMethod,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Response:
        raise NotImplementedError

    async def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Response:
        return await self.request(url, "get", headers=headers, **kwargs)

    async def post(
        self,
        url: str,
        data: RequestData | None = None,
        json: JSON | None = None,
        files: dict[str, UploadedFile] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Response:
        return await self.request(
            url,
            "post",
            headers=headers,
            data=data,
            json=json,
            files=files,
            **kwargs,
        )


def merge_cookies(
    headers: dict[str, str] | None, cookies: Mapping[str, str] | None
) -> dict[str, str] | None:
    if not cookies:
        return headers

    merged_headers = dict(headers or {})
    existing_cookie_header = merged_headers.pop("Cookie", "")
    existing_cookies: dict[str, str] = {}

    for cookie in existing_cookie_header.split(";"):
        name, separator, value = cookie.strip().partition("=")
        if separator and name:
            existing_cookies[name] = value

    combined_cookies = {**existing_cookies, **cookies}
    merged_headers["Cookie"] = "; ".join(
        f"{name}={value}" for name, value in combined_cookies.items()
    )
    return merged_headers
