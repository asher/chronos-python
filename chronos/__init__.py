#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2014 Asher Feldman
# Derived in part from work by Chris Zacharias (chris@imgix.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import httplib2
import socket
import json
import logging
import warnings

# Python 3 changed the submodule for quote
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

SCHEDULER_API_VERSIONS = ('v1',)


class ChronosError(Exception):
    pass


class ChronosAPIError(ChronosError):
    pass


class UnauthorizedError(ChronosAPIError):
    pass


class ChronosValidationError(ChronosError):
    pass


class MissingFieldError(ChronosValidationError):
    pass


class OneOfViolationError(ChronosValidationError):
    pass


class ChronosClient(object):
    _user = None
    _password = None

    def __init__(
        self, servers, proto="http", username=None, password=None,
        extra_headers=None, scheduler_api_version='v1',
        validate_ssl_certificates=True,
    ):
        server_list = servers if isinstance(servers, list) else [servers]
        self.servers = ["%s://%s" % (proto, server) for server in server_list]
        self.extra_headers = extra_headers
        if username and password:
            self._user = username
            self._password = password
        self.logger = logging.getLogger(__name__)
        if scheduler_api_version is None:
            warnings.warn("Chronos >=3.x requires scheduler_api_version set", FutureWarning)
            self._prefix = ''
        else:
            if scheduler_api_version not in SCHEDULER_API_VERSIONS:
                raise ChronosAPIError('Wrong scheduler_api_version provided')
            self._prefix = "/%s" % (scheduler_api_version,)
        self.scheduler_api_version = scheduler_api_version
        self.disable_ssl_certificate_validation = not validate_ssl_certificates

    def list(self):
        """List all jobs on Chronos."""
        return self._call("/scheduler/jobs", "GET")

    def delete(self, name):
        """Delete a job by name"""
        path = "/scheduler/job/%s" % name
        return self._call(path, "DELETE")

    def delete_tasks(self, name):
        """Terminate all tasks for a running/stuck job"""
        path = "/scheduler/task/kill/%s" % name
        return self._call(path, "DELETE")

    def run(self, name):
        """Run a job by name"""
        path = "/scheduler/job/%s" % name
        return self._call(path, "PUT")

    def add(self, job_def, update=False):
        """Schedule a new job"""
        path = "/scheduler/iso8601"
        self._check_fields(job_def)
        if "parents" in job_def:
            path = "/scheduler/dependency"
        # Cool story: chronos >= 3.0 ditched PUT and only allows POST here,
        # trying to maintain backwards compat with < 3.0
        method = "POST"
        if self.scheduler_api_version is None:
            if update:
                method = "PUT"
            else:
                method = "POST"
        return self._call(path, method, json.dumps(job_def))

    def update(self, job_def):
        """Update an existing job by name"""
        return self.add(job_def, update=True)

    def job_stat(self, name):
        """ List stats for a job """
        return self._call('/scheduler/job/stat/%s' % name, "GET")

    def scheduler_graph(self):
        return self._call('/scheduler/graph/csv', 'GET')

    def scheduler_stat_99th(self):
        return self._call('/scheduler/stats/99thPercentile', 'GET')

    def scheduler_stat_98th(self):
        return self._call('/scheduler/stats/98thPercentile', 'GET')

    def scheduler_stat_95th(self):
        return self._call('/scheduler/stats/95thPercentile', 'GET')

    def scheduler_stat_75th(self):
        return self._call('/scheduler/stats/75thPercentile', 'GET')

    def scheduler_stat_median(self):
        return self._call('/scheduler/stats/median', 'GET')

    def scheduler_stat_mean(self):
        return self._call('/scheduler/stats/mean', 'GET')

    def metrics(self):
        # for some reason, /metrics is not prefixed with the version
        return self._call('/metrics', 'GET', prefix=False)

    def _call(self, url, method="GET", body=None, headers={}, prefix=True):
        hdrs = {}
        if body:
            hdrs['Content-Type'] = "application/json"
        hdrs.update(headers)
        if prefix:
            _url = '%s%s' % (self._prefix, url, )
        else:
            _url = url
        self.logger.debug("Calling: %s %s" % (method, _url))
        if body:
            self.logger.debug("Body: %s" % body)
        conn = httplib2.Http(disable_ssl_certificate_validation=self.disable_ssl_certificate_validation)
        if self._user and self._password:
            conn.add_credentials(self._user, self._password)
        if self.extra_headers:
            hdrs.update(self.extra_headers)

        response = None
        servers = list(self.servers)
        while servers:
            server = servers.pop(0)
            endpoint = "%s%s" % (server, quote(_url))
            try:
                resp, content = conn.request(endpoint, method, body=body, headers=hdrs)
            except (socket.error, httplib2.ServerNotFoundError) as e:
                self.logger.error('Error while calling %s: %s. Retrying', endpoint, e.message)
                continue
            try:
                response = self._check(resp, content)
                return response
            except ChronosAPIError as e:
                self.logger.error('Error while calling %s: %s', endpoint, e.message)

        raise ChronosAPIError('No remaining Chronos servers to try')

    def _check(self, resp, content):
        status = resp.status
        self.logger.debug("status: %d" % status)
        payload = None

        if status == 401:
            raise UnauthorizedError()

        if content:
            try:
                payload = json.loads(content.decode('utf-8'))
            except ValueError:
                if resp['content-type'] == "application/json":
                    self.logger.error("Response not valid json: %s" % content)
                payload = content

        if payload is None and status != 204:
            raise ChronosAPIError("Request to Chronos API failed: status: %d, response: %s" % (status, content))

        # if the status returned is not an OK status, raise an exception
        if status >= 400:
            message = "API returned status %d, content: %s" % (status, payload,)
            # newer chronos does return the full stack trace in a message field,
            # grabbing the first 160 chars from it
            if 'message' in payload:
                self.logger.debug(payload['message'])
                message = '%s (...)' % (payload['message'][:120],)
            raise ChronosAPIError(message)

        return payload

    def _check_fields(self, job):
        fields = ChronosJob.fields
        if self.scheduler_api_version is None:
            fields.extend(ChronosJob.legacy_fields)
        for k in fields:
            if k not in job:
                raise MissingFieldError("missing required field %s" % k)

        if any(field in job for field in ChronosJob.one_of):
            if len([field for field in ChronosJob.one_of if field in job]) > 1:
                raise OneOfViolationError("Job must only include 1 of %s" % ChronosJob.one_of)
        else:
            raise MissingFieldError("Job must include one of %s" % ChronosJob.one_of)

        if "container" in job:
            container = job["container"]
            for k in ChronosJob.container_fields:
                if k not in container:
                    raise MissingFieldError("missing required container field %s" % k)

        return True


class ChronosJob(object):
    fields = [
        "command",
        "name",
        "owner",
        "disabled"
    ]
    legacy_fields = [
        "async",
    ]
    one_of = ["schedule", "parents"]
    container_fields = [
        "type",
        "image"
    ]


def connect(servers, proto="http", username=None, password=None, extra_headers=None, scheduler_api_version='v1'):
    return ChronosClient(
        servers, proto=proto, username=username, password=password,
        extra_headers=extra_headers, scheduler_api_version=scheduler_api_version
    )
