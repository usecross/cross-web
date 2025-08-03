from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Optional, Union, cast

from ._base import FormData, HTTPMethod, QueryParams, SyncHTTPRequestAdapter

if TYPE_CHECKING:
    from chalice.app import Request


class ChaliceHTTPRequestAdapter(SyncHTTPRequestAdapter):
    def __init__(self, request: Request) -> None:
        self.request = request

    @property
    def query_params(self) -> QueryParams:
        return self.request.query_params or {}

    @property
    def body(self) -> Union[str, bytes]:
        return self.request.raw_body

    @property
    def method(self) -> HTTPMethod:
        return cast("HTTPMethod", self.request.method.upper())

    @property
    def headers(self) -> Mapping[str, str]:
        return self.request.headers

    @property
    def post_data(self) -> Mapping[str, Union[str, bytes]]:
        # Chalice doesn't support traditional form data
        raise NotImplementedError("Chalice does not support form data")

    @property
    def files(self) -> Mapping[str, Any]:
        # Chalice doesn't support file uploads out of the box
        raise NotImplementedError("Chalice does not support file uploads")

    def get_form_data(self) -> FormData:
        # Chalice doesn't support form data
        raise NotImplementedError("Chalice does not support form data")

    @property
    def content_type(self) -> Optional[str]:
        return self.request.headers.get("Content-Type", None)

    @property
    def url(self) -> str:
        # Construct URL from context
        context = self.request.context
        stage = context.get("stage", "")
        domain = context.get("domainName", "")
        path = context.get("path", "")

        # Build the URL
        protocol = "https"  # API Gateway typically uses HTTPS
        if stage and stage != "prod":
            url = f"{protocol}://{domain}/{stage}{path}"
        else:
            url = f"{protocol}://{domain}{path}"

        # Add query string if present
        if self.request.query_params:
            from urllib.parse import urlencode

            query_string = urlencode(self.request.query_params)
            url = f"{url}?{query_string}"

        return url

    @property
    def cookies(self) -> Mapping[str, str]:
        # Chalice doesn't have direct cookie support
        # Cookies would come in the Cookie header
        cookie_header = self.request.headers.get("Cookie", "")
        if not cookie_header:
            return {}

        cookies = {}
        for cookie in cookie_header.split(";"):
            cookie = cookie.strip()
            if "=" in cookie:
                name, value = cookie.split("=", 1)
                cookies[name] = value

        return cookies
