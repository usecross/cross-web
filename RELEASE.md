Release type: patch

`Response.redirect` now merges `query_params` into a URL that already has a
query string instead of appending a second `?` to it, so
`Response.redirect("/cb?a=1", {"code": "x"})` redirects to `/cb?a=1&code=x`.
A fragment stays after the query, including an empty `#`, and a list value is
repeated as `key=a&key=b` rather than encoded as a Python list.
