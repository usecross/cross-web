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
    from django.http import HttpRequest


class DjangoHTTPRequestAdapter(SyncHTTPRequestAdapter):
    def __init__(self, request: HttpRequest) -> None:
        self.request = request

    @property
    def query_params(self) -> QueryParams:
        return cast(QueryParams, self.request.GET.dict())

    @property
    def body(self) -> Union[str, bytes]:
        return cast(Union[str, bytes], self.request.body.decode())

    @property
    def method(self) -> HTTPMethod:
        assert self.request.method is not None

        return cast("HTTPMethod", self.request.method.upper())

    @property
    def headers(self) -> Mapping[str, str]:
        return cast(Mapping[str, str], self.request.headers)

    @property
    def post_data(self) -> Mapping[str, Union[str, bytes]]:
        return cast(Mapping[str, Union[str, bytes]], self.request.POST)

    @property
    def files(self) -> Mapping[str, Any]:
        return cast(Mapping[str, Any], self.request.FILES)

    def get_form_data(self) -> FormData:
        return FormData(
            files=cast(Mapping[str, Any], self.request.FILES),
            form=cast(Mapping[str, Union[str, bytes]], self.request.POST),
        )

    @property
    def content_type(self) -> Optional[str]:
        return cast(Optional[str], self.request.content_type)

    @property
    def url(self) -> str:
        return cast(str, self.request.build_absolute_uri())

    @property
    def cookies(self) -> Mapping[str, str]:
        return cast(Mapping[str, str], self.request.COOKIES)


class AsyncDjangoHTTPRequestAdapter(AsyncHTTPRequestAdapter):
    def __init__(self, request: HttpRequest) -> None:
        self.request = request

    @property
    def query_params(self) -> QueryParams:
        return cast(QueryParams, self.request.GET.dict())

    @property
    def method(self) -> HTTPMethod:
        assert self.request.method is not None

        return cast("HTTPMethod", self.request.method.upper())

    @property
    def headers(self) -> Mapping[str, str]:
        return cast(Mapping[str, str], self.request.headers)

    @property
    def content_type(self) -> Optional[str]:
        return self.headers.get("Content-type")

    async def get_body(self) -> bytes:
        return cast(bytes, self.request.body)

    async def get_form_data(self) -> FormData:
        return FormData(
            files=cast(Mapping[str, Any], self.request.FILES),
            form=cast(Mapping[str, Union[str, bytes]], self.request.POST),
        )

    @property
    def url(self) -> str:
        return cast(str, self.request.build_absolute_uri())

    @property
    def cookies(self) -> Mapping[str, str]:
        return cast(Mapping[str, str], self.request.COOKIES)
