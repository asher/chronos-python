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


def test_uses_server_list():
    client = chronos.ChronosClient(["host1", "host2", "host3"], proto="http")
    good_request = (mock.Mock(status=204), '')
    bad_request = (mock.Mock(status=500), '')

    conn_mock = mock.Mock(request=mock.Mock(side_effect=[bad_request, good_request, bad_request]))
    with mock.patch('httplib2.Http', return_value=conn_mock):
        client._call('/fake_url')
        assert conn_mock.request.call_count == 2
