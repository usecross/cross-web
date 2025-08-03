import json
import pytest
from lia.exceptions import HTTPException
from lia.json_utils import decode_json, encode_json, parse_json


def test_parse_json_valid_string():
    data = '{"key": "value", "number": 123}'
    result = parse_json(data)
    assert result == {"key": "value", "number": 123}


def test_parse_json_valid_bytes():
    data = b'{"key": "value", "number": 123}'
    result = parse_json(data)
    assert result == {"key": "value", "number": 123}


def test_parse_json_invalid_json():
    with pytest.raises(HTTPException) as exc_info:
        parse_json('{"invalid": json}')
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.reason == "Unable to parse request body as JSON"


def test_parse_json_empty_string():
    with pytest.raises(HTTPException) as exc_info:
        parse_json('')
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.reason == "Unable to parse request body as JSON"


def test_parse_json_array():
    data = '[1, 2, 3, "test"]'
    result = parse_json(data)
    assert result == [1, 2, 3, "test"]


def test_decode_json_string():
    data = '{"test": true, "value": null}'
    result = decode_json(data)
    assert result == {"test": True, "value": None}


def test_decode_json_bytes():
    data = b'{"test": false, "number": 3.14}'
    result = decode_json(data)
    assert result == {"test": False, "number": 3.14}


def test_decode_json_invalid():
    with pytest.raises(json.JSONDecodeError):
        decode_json('not json')


def test_encode_json_dict():
    data = {"key": "value", "number": 42}
    result = encode_json(data)
    assert result == '{"key": "value", "number": 42}'


def test_encode_json_list():
    data = [1, 2, "three", None, True]
    result = encode_json(data)
    assert result == '[1, 2, "three", null, true]'


def test_encode_json_nested():
    data = {
        "nested": {"inner": [1, 2, 3]},
        "array": [{"id": 1}, {"id": 2}]
    }
    result = encode_json(data)
    parsed = json.loads(result)
    assert parsed == data


def test_encode_json_empty():
    assert encode_json({}) == '{}'
    assert encode_json([]) == '[]'
    assert encode_json(None) == 'null'
    assert encode_json("") == '""'