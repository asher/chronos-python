import json

import mock
import pytest
import httplib2

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


def test_api_error_throws_exception():
    client = chronos.ChronosClient(hostname="localhost")
    mock_response = mock.Mock()
    mock_response.status = 500
    mock_request = mock.Mock(return_value=(mock_response, None))
    with mock.patch.object(httplib2.Http, 'request', mock_request):
        with pytest.raises(chronos.ChronosAPIException):
            client.list()


def test_check_missing_fields():
    client = chronos.ChronosClient(hostname="localhost")
    for field in chronos.ChronosJob.fields:
        without_field = {x: 'foo' for x in filter(lambda y: y != field, chronos.ChronosJob.fields)}
        with pytest.raises(chronos.MissingFieldException):
            client._check_fields(without_field)


def test_check_one_of():
    client = chronos.ChronosClient(hostname="localhost")
    job = {field: 'foo' for field in chronos.ChronosJob.fields}
    with pytest.raises(chronos.MissingFieldException):
        client._check_fields(job)
