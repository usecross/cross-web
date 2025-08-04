from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Optional, Union, cast

from ._base import (
    AsyncHTTPRequestAdapter,
    FormData,
    HTTPMethod,
    QueryParams,
    SyncHTTPRequestAdapter,
)

if TYPE_CHECKING:
    from flask import Request


class FlaskHTTPRequestAdapter(SyncHTTPRequestAdapter):
    def __init__(self, request: Request) -> None:
        self.request = request

    @property
    def query_params(self) -> QueryParams:
        return self.request.args.to_dict()

    @property
    def body(self) -> Union[str, bytes]:
        return self.request.data.decode()

    @property
    def method(self) -> HTTPMethod:
        return cast("HTTPMethod", self.request.method.upper())

    @property
    def headers(self) -> Mapping[str, str]:
        return self.request.headers  # type: ignore

    @property
    def post_data(self) -> Mapping[str, Union[str, bytes]]:
        return self.request.form

    @property
    def files(self) -> Mapping[str, Any]:
        return self.request.files

    def get_form_data(self) -> FormData:
        return FormData(
            files=self.request.files,
            form=self.request.form,
        )

    @property
    def content_type(self) -> Optional[str]:
        return self.request.content_type

    @property
    def url(self) -> str:
        return self.request.url

    @property
    def cookies(self) -> Mapping[str, str]:
        return self.request.cookies


class AsyncFlaskHTTPRequestAdapter(AsyncHTTPRequestAdapter):
    def __init__(self, request: Request) -> None:
        self.request = request

    @property
    def query_params(self) -> QueryParams:
        return self.request.args.to_dict()

    @property
    def method(self) -> HTTPMethod:
        return cast("HTTPMethod", self.request.method.upper())

    @property
    def content_type(self) -> Optional[str]:
        return self.request.content_type

    @property
    def headers(self) -> Mapping[str, str]:
        return self.request.headers  # type: ignore

    async def get_body(self) -> bytes:
        return self.request.data

    async def get_form_data(self) -> FormData:
        return FormData(
            files=self.request.files,
            form=self.request.form,
        )

    @property
    def url(self) -> str:
        return self.request.url

    @property
    def cookies(self) -> Mapping[str, str]:
        return self.request.cookies
