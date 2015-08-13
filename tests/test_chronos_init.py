import json
import mock

import chronos


def test_connect_accepts_single_host():
    client = chronos.ChronosClient("localhost", proto="http")
    assert client.servers == ['http://localhost']


def test_connect_accepts_list_of_hosts():
    client = chronos.ChronosClient(["host1", "host2"], proto="http")
    assert client.servers == ['http://host1', 'http://host2']


def test_connect_accepts_proto():
    client = chronos.ChronosClient("localhost", proto="fake_proto")
    assert client.servers == ['fake_proto://localhost']


def test_check_accepts_json():
    client = chronos.ChronosClient("localhost")
    fake_response = mock.Mock()
    fake_response.status = 200
    fake_content = '{ "foo": "bar" }'
    actual = client._check(fake_response, fake_content)
    assert actual == json.loads(fake_content)


def test_check_returns_raw_response_when_not_json():
    client = chronos.ChronosClient("localhost")
    fake_response = mock.Mock()
    fake_response.status = 401
    fake_content = 'UNAUTHORIZED'
    actual = client._check(fake_response, fake_content)
    assert actual == fake_content
