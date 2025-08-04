from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Optional, Union, cast

from ._base import AsyncHTTPRequestAdapter, FormData, HTTPMethod, QueryParams

if TYPE_CHECKING:
    from sanic.request import File, Request


def convert_request_to_files_dict(request: Request) -> dict[str, Any]:
    """Converts the request.files dictionary to a dictionary of sanic Request objects.

    `request.files` has the following format, even if only a single file is uploaded:

    ```python
    {
        "textFile": [
            sanic.request.File(type="text/plain", body=b"strawberry", name="textFile.txt")
        ]
    }
    ```

    Note that the dictionary entries are lists.
    """
    request_files = cast("Optional[dict[str, list[File]]]", request.files)

    if not request_files:
        return {}

    files_dict: dict[str, Union[File, list[File]]] = {}

    for field_name, file_list in request_files.items():
        assert len(file_list) == 1

        files_dict[field_name] = file_list[0]

    return files_dict


class SanicHTTPRequestAdapter(AsyncHTTPRequestAdapter):
    def __init__(self, request: Request) -> None:
        self.request = request

    @property
    def query_params(self) -> QueryParams:
        # Just a heads up, Sanic's request.args uses urllib.parse.parse_qs
        # to parse query string parameters. This returns a dictionary where
        # the keys are the unique variable names and the values are lists
        # of values for each variable name. To ensure consistency, we're
        # enforcing the use of the first value in each list.
        args = self.request.get_args(keep_blank_values=True)
        return {k: args.get(k, None) for k in args}

    @property
    def method(self) -> HTTPMethod:
        return cast("HTTPMethod", self.request.method.upper())

    @property
    def headers(self) -> Mapping[str, str]:
        return self.request.headers

    @property
    def content_type(self) -> Optional[str]:
        return self.request.content_type

    async def get_body(self) -> bytes:
        return self.request.body

    async def get_form_data(self) -> FormData:
        assert self.request.form is not None

        files = convert_request_to_files_dict(self.request)

        return FormData(form=self.request.form, files=files)

    @property
    def url(self) -> str:
        return self.request.url

    @property
    def cookies(self) -> Mapping[str, str]:
        return self.request.cookies
