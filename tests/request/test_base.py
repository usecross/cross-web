from cross_web.request._base import FormData


def test_form_data_creation() -> None:
    files = {"file1": "content1"}
    form = {"field1": "value1", "field2": "value2"}

    form_data = FormData(files=files, form=form)

    assert form_data.files == files
    assert form_data.form == form


def test_form_data_get_existing_key() -> None:
    form_data = FormData(
        files={"upload": "data"}, form={"username": "john", "email": "john@example.com"}
    )

    assert form_data.get("username") == "john"
    assert form_data.get("email") == "john@example.com"


def test_form_data_get_missing_key() -> None:
    form_data = FormData(files={}, form={"name": "test"})

    assert form_data.get("missing") is None


def test_form_data_get_from_files() -> None:
    # The get method only retrieves from form, not files
    form_data = FormData(
        files={"file_key": "file_value"}, form={"form_key": "form_value"}
    )

    assert form_data.get("form_key") == "form_value"
    assert form_data.get("file_key") is None  # Files are not accessed via get()


def test_form_data_empty() -> None:
    form_data = FormData(files={}, form={})

    assert form_data.files == {}
    assert form_data.form == {}
    assert form_data.get("anything") is None
