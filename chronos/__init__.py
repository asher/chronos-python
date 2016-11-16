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

# Python 3 changed the submodule for quote
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


class ChronosAPIError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class MissingFieldError(Exception):
    pass


class OneOfViolationError(Exception):
    pass


class ChronosClient(object):
    _user = None
    _password = None

    def __init__(self, servers, proto="http", username=None, password=None, extra_headers=None, level='WARN'):
        server_list = servers if isinstance(servers, list) else [servers]
        self.servers = ["%s://%s" % (proto, server) for server in server_list]
        self.extra_headers = extra_headers
        if username and password:
            self._user = username
            self._password = password
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=level)
        self.logger = logging.getLogger(__name__)

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
        return self._call('/metrics', 'GET')

    def _call(self, url, method="GET", body=None, headers={}):
        hdrs = {}
        if body:
            hdrs['Content-Type'] = "application/json"
        hdrs.update(headers)
        self.logger.debug("Fetch: %s %s" % (method, url))
        if body:
            self.logger.debug("Body: %s" % body)
        conn = httplib2.Http(disable_ssl_certificate_validation=True)
        if self._user and self._password:
            conn.add_credentials(self._user, self._password)
        if self.extra_headers:
            hdrs.update(self.extra_headers)

        response = None
        servers = list(self.servers)
        while servers:
            server = servers.pop(0)
            endpoint = "%s%s" % (server, quote(url))
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

        return payload

    def _check_fields(self, job):
        for k in ChronosJob.fields:
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
        "async",
        "command",
        "name",
        "owner",
        "disabled"
    ]
    one_of = ["schedule", "parents"]
    container_fields = [
        "type",
        "image"
    ]


def connect(servers, proto="http", username=None, password=None, extra_headers=None):
    return ChronosClient(servers, proto=proto, username=username, password=password, extra_headers=extra_headers)
