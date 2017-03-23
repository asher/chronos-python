import json
import mock
import pytest
import httplib2

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


def test_http_codes():
    client = chronos.ChronosClient("localhost")
    fake_response = mock.Mock()
    # all status codes 2xx and 3xx are potentially valid
    valid_codes = range(200, 399)
    for status in valid_codes:
        fake_response.status = status
        fake_content = '{ "foo": "bar" }'
        actual = client._check(fake_response, fake_content)
        assert actual == json.loads(fake_content)
    # we treat 401 in a special way, so we skip it (add 400 at the beginning)
    invalid_codes = range(402, 550)
    invalid_codes.insert(0, 400)
    for status in invalid_codes:
        fake_response.status = status
        fake_content = '{ "foo": "bar" }'
        with pytest.raises(chronos.ChronosAPIError):
            actual = client._check(fake_response, fake_content)
    # let's test 401 finally
    fake_response.status = 401
    fake_content = '{ "foo": "bar" }'
    with pytest.raises(chronos.UnauthorizedError):
        actual = client._check(fake_response, fake_content)


def test_check_returns_raw_response_when_not_json():
    client = chronos.ChronosClient("localhost")
    fake_response = mock.Mock(__getitem__=mock.Mock(return_value="not-json"))
    fake_response.status = 400
    fake_content = 'foo bar baz'
    try:
        actual = client._check(fake_response, fake_content)
    except chronos.ChronosAPIError as cap:
        actual = cap.message
    # on exceptions, the content is passed on the exception's message
    assert actual == "API returned status 400, content: %s" % (fake_content, )


def test_check_does_not_log_error_when_content_type_is_not_json():
    with mock.patch('logging.getLogger', return_value=mock.Mock(error=mock.Mock())) as mock_log:
        client = chronos.ChronosClient("localhost")
        fake_response = mock.Mock(__getitem__=mock.Mock(return_value="not-json"))
        fake_response.status = 400
        fake_content = 'foo bar baz'
        try:
            client._check(fake_response, fake_content)
        except chronos.ChronosAPIError as cap:
            pass
        assert mock_log().error.call_count == 0


def test_check_logs_error_when_invalid_json():
    with mock.patch('logging.getLogger', return_value=mock.Mock(error=mock.Mock())) as mock_log:
        client = chronos.ChronosClient("localhost")
        fake_response = mock.Mock(__getitem__=mock.Mock(return_value="application/json"))
        fake_response.status = 400
        fake_content = 'foo bar baz'
        try:
            client._check(fake_response, fake_content)
        except chronos.ChronosAPIError as cap:
            pass
        mock_log().error.assert_called_once_with("Response not valid json: %s" % fake_content)


def test_uses_server_list():
    client = chronos.ChronosClient(["host1", "host2", "host3"], proto="http")
    good_request = (mock.Mock(status=204), '')
    bad_request = (mock.Mock(status=500), '')

    conn_mock = mock.Mock(request=mock.Mock(side_effect=[bad_request, good_request, bad_request]))
    with mock.patch('httplib2.Http', return_value=conn_mock):
        client._call('/fake_url')
        assert conn_mock.request.call_count == 2


def test_api_error_throws_exception():
    client = chronos.ChronosClient(servers="localhost")
    mock_response = mock.Mock()
    mock_response.status = 500
    mock_request = mock.Mock(return_value=(mock_response, None))
    with mock.patch.object(httplib2.Http, 'request', mock_request):
        with pytest.raises(chronos.ChronosAPIError):
            client.list()


def test_check_missing_top_level_fields():
    client = chronos.ChronosClient(servers="localhost")
    for field in chronos.ChronosJob.fields:
        without_field = {x: 'foo' for x in filter(lambda y: y != field, chronos.ChronosJob.fields)}
        with pytest.raises(chronos.MissingFieldError):
            client._check_fields(without_field)


def test_check_missing_container_fields():
    client = chronos.ChronosClient(servers="localhost")
    for field in chronos.ChronosJob.container_fields:
        container_without_field = {x: 'foo' for x in filter(lambda y: y != field, chronos.ChronosJob.container_fields)}
        job_def = {
            "container": container_without_field,
            "command": "while sleep 10; do date =u %T; done",
            "schedule": "R/2014-09-25T17:22:00Z/PT2M",
            "name": "dockerjob",
            "owner": "test",
            "disabled": False
        }
        with pytest.raises(chronos.MissingFieldError) as excinfo:
            client._check_fields(job_def)
        assert field in str(excinfo.value)


def test_check_one_of_missing():
    client = chronos.ChronosClient(servers="localhost")
    job = {field: 'foo' for field in chronos.ChronosJob.fields}
    with pytest.raises(chronos.MissingFieldError):
        client._check_fields(job)


def test_check_one_of_all():
    client = chronos.ChronosClient(servers="localhost")
    job = {field: 'foo' for field in (chronos.ChronosJob.fields + chronos.ChronosJob.one_of)}
    with pytest.raises(chronos.OneOfViolationError):
        client._check_fields(job)


def test_check_unauthorized_raises():
    client = chronos.ChronosClient(servers="localhost")
    mock_response = mock.Mock()
    mock_response.status = 401
    with pytest.raises(chronos.UnauthorizedError):
        client._check(mock_response, '{"foo": "bar"}')


@mock.patch('chronos.ChronosJob')
def test_check_one_of_ok(patch_chronos_job):
    patch_chronos_job.one_of = ['foo', 'bar']
    patch_chronos_job.fields = ['field1', 'field2']
    job = {field: 'foo' for field in chronos.ChronosJob.fields}
    client = chronos.ChronosClient(servers="localhost")
    for one_of_field in ['foo', 'bar']:
        complete = job.copy()
        complete.update({one_of_field: 'val'})
        assert client._check_fields(complete)


@mock.patch('chronos.ChronosJob')
def test_check_one_of_more_than_one(patch_chronos_job):
    patch_chronos_job.one_of = ['foo', 'bar', 'baz']
    patch_chronos_job.fields = ['field1', 'field2']
    job = {field: 'foo' for field in (chronos.ChronosJob.fields + ['foo', 'bar'])}
    client = chronos.ChronosClient(servers="localhost")
    with pytest.raises(chronos.OneOfViolationError):
        client._check_fields(job)


@mock.patch('chronos.httplib2.Http')
def test_call_retries_on_http_error(mock_http):
    mock_call = mock.Mock(side_effect=[
        httplib2.socket.error,
        httplib2.ServerNotFoundError,
        (mock.Mock(status=200), '{"foo": "bar"}')
    ])
    mock_http.return_value = mock.Mock(
            request=mock_call
    )
    client = chronos.ChronosClient(servers=['1.2.3.4', '1.2.3.5', '1.2.3.6'])
    client._call("/foo")
    mock_call.assert_any_call('http://1.2.3.4%s/foo' % client._prefix, 'GET', body=None, headers={})
    mock_call.assert_any_call('http://1.2.3.5%s/foo' % client._prefix, 'GET', body=None, headers={})
    mock_call.assert_any_call('http://1.2.3.6%s/foo' % client._prefix, 'GET', body=None, headers={})
