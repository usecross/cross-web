from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


@dataclass
class JSONRequestResult:
    query_params: dict[str, Any]
    method: str
    header_content_type: str | None
    content_type: str | None
    url_path: str
    url_query: str
    cookies: dict[str, str]
    body_json: dict[str, Any]


@dataclass
class FormRequestResult:
    query_params: dict[str, Any]
    method: str
    header_content_type: str | None
    content_type: str | None
    url_path: str
    url_query: str
    cookies: dict[str, str]
    form_value: str
    has_file: bool
    post_form_value: str | None = None
    files_has_file: bool | None = None


class RequestClient(abc.ABC):
    supports_form_data = True

    @abc.abstractmethod
    async def json_request(self) -> JSONRequestResult:
        raise NotImplementedError

    @abc.abstractmethod
    async def form_request(self) -> FormRequestResult:
        raise NotImplementedError


def get_content_type(headers: dict[str, Any]) -> str | None:
    return headers.get("content-type") or headers.get("Content-Type")


def normalize_cookies(cookies: dict[str, Any]) -> dict[str, str]:
    normalized = {}
    for key, value in cookies.items():
        if isinstance(value, list):
            normalized[key] = str(value[0])
        else:
            normalized[key] = str(value)
    return normalized


def normalize_value(value: Any) -> str:
    if isinstance(value, list):
        return normalize_value(value[0])

    if isinstance(value, bytes):
        return value.decode()

    return str(value)


def build_json_result(data: dict[str, Any]) -> JSONRequestResult:
    parsed_url = urlparse(data["url"])

    return JSONRequestResult(
        query_params=data["query_params"],
        method=data["method"],
        header_content_type=data["header_content_type"],
        content_type=data["content_type"],
        url_path=parsed_url.path,
        url_query=parsed_url.query,
        cookies=normalize_cookies(data["cookies"]),
        body_json=data["body_json"],
    )


def build_form_result(data: dict[str, Any]) -> FormRequestResult:
    parsed_url = urlparse(data["url"])

    return FormRequestResult(
        query_params=data["query_params"],
        method=data["method"],
        header_content_type=data["header_content_type"],
        content_type=data["content_type"],
        url_path=parsed_url.path,
        url_query=parsed_url.query,
        cookies=normalize_cookies(data["cookies"]),
        form_value=normalize_value(data["form_value"]),
        has_file=bool(data["has_file"]),
        post_form_value=(
            normalize_value(data["post_form_value"])
            if data.get("post_form_value") is not None
            else None
        ),
        files_has_file=(
            bool(data["files_has_file"])
            if data.get("files_has_file") is not None
            else None
        ),
    )
