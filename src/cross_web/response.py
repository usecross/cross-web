from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Mapping, List, Union, cast
from typing_extensions import Self
from urllib.parse import urlencode

if TYPE_CHECKING:
    from fastapi import Response as FastAPIResponse

JsonType = Union[
    str, int, float, bool, None, Mapping[str, "JsonType"], List["JsonType"]
]


@dataclass
class Cookie:
    name: str
    value: str
    secure: bool
    path: str | None = None
    domain: str | None = None
    max_age: int | None = None
    httponly: bool = True
    samesite: Literal["lax", "strict", "none"] = "lax"


@dataclass
class Response:
    status_code: int
    body: str | None = None
    cookies: list[Cookie] | None = None
    headers: Mapping[str, str] | None = None

    @classmethod
    def redirect(
        cls,
        url: str,
        query_params: Mapping[str, str | list[str]] | None = None,
        headers: Mapping[str, str] | None = None,
        cookies: list[Cookie] | None = None,
    ) -> Self:
        headers = headers or {}

        if query_params:
            url = url + "?" + urlencode(query_params)

        return cls(
            status_code=302,
            headers={"Location": url, **headers},
            cookies=cookies,
        )

    def json(self) -> JsonType:
        if self.body is None:
            return None

        return cast(JsonType, json.loads(self.body))

    def to_fastapi(self) -> FastAPIResponse:
        from fastapi import Response as FastAPIResponse

        response = FastAPIResponse(
            status_code=self.status_code,
            headers=self.headers,
            content=self.body,
        )

        for cookie in self.cookies or []:
            response.set_cookie(
                cookie.name,
                cookie.value,
                secure=cookie.secure,
                path=cookie.path,
                domain=cookie.domain,
                max_age=cookie.max_age,
                httponly=cookie.httponly,
                samesite=cookie.samesite,
            )

        return response
