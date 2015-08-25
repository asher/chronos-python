import json

import mock

import chronos


def test_check_accepts_json():
    client = chronos.ChronosClient(hostname="localhost")
    fake_response = mock.Mock()
    fake_response.status = 200
    fake_content = '{ "foo": "bar" }'
    actual = client._check(fake_response, fake_content)
    assert actual == json.loads(fake_content)


def test_check_returns_raw_response_when_not_json():
    client = chronos.ChronosClient(hostname="localhost")
    fake_response = mock.Mock()
    fake_response.status = 401
    fake_content = 'UNAUTHORIZED'
    actual = client._check(fake_response, fake_content)
    assert actual == fake_content
