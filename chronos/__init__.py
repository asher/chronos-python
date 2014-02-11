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
import json


class ChronosClient(object):
    _user = None
    _password = None

    def __init__(self, hostname, proto="http", username=None, password=None):
        self.baseurl = "%s://%s" % (proto, hostname)
        if username and password:
            self._user = username
            self._password = password

    def list(self):
        """List all jobs on Chronos."""
        return self._call("/scheduler/jobs", "GET")

    def delete_job(self, name):
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
        if update:
            method = "PUT"
        else:
            method = "POST"
        return self._call(path, method, json.dumps(job_def))

    def update(self, job_def):
        """Update an existing job by name"""
        return self.add(job_def, update=True)

    def _call(self, url, method="GET", body=None, headers={}):
        hdrs = {}
        if body:
            hdrs['Content-Type'] = "application/json"
        hdrs.update(headers)
        print "Fetch: %s %s" % (method, url)
        if body:
            print "Body: %s" % body
        conn = httplib2.Http(disable_ssl_certificate_validation=True)
        if self._user and self._password:
            conn.add_credentials(self._user, self._password)
        endpoint = "%s%s" % (self.baseurl, url)
        print endpoint
        return self._check(*conn.request(endpoint, method, body=body, headers=hdrs))

    def _check(self, resp, content):
        status = resp.status
        print "status: %d" % status
        payload = None
        if content:
            try:
                payload = json.loads(content)
            except ValueError:
                print "Response not valid json: %s" % content
                payload = content

        if payload is None and status != 204:
            raise Exception("HTTP Error %d occurred." % status)

        return payload

    def _check_fields(self, job):
        for k in ChronosJob.fields:
            if k not in job:
                raise Exception("missing required field %s" % k)
        for k in ChronosJob.one_of:
            if k in job:
                return True
            else:
                raise Exception("Job must include one of %s" % ChronosJob.one_of)


class ChronosJob(object):
    fields = [
        "async",
        "command",
        "epsilon",
        "name",
        "owner",
        "disabled"
    ]
    one_of = ["schedule", "parents"]


def connect(hostname, proto="http", username=None, password=None):
    return ChronosClient(hostname, proto="http", username=None, password=None)
