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
        return self._call("/scheduler/jobs", "GET")

    def delete_job(self, name):
        path = "/scheduler/job/%s" % name
        return self._call(path, "DELETE")

    def delete_tasks(self, name):
        path = "/scheduler/task/kill/%s" % name
        return self._call(path, "DELETE")

    def run(self, name):
        path = "/scheduler/job/%s" % name
        return self._call(path, "PUT")

    def add(self, job_def, update=False):
        path = "/scheduler/iso8601"
        for k in ChronosJob.fields:
            if k not in job_def:
                raise Exception("Job missing required field %s" % k)
            if "schedule" not in job_def and "parents" not in job_def:
                raise Exception("Job must have a schedule or a parent")
        if update:
            method = "PUT"
        else:
            method = "POST"
        return self._call(path, method, json.dumps(job_def))

    def update(self, job_def):
        return self.add(job_def, update=True)

    def _call(self, url, method="GET", body=None, headers={}):
        hdrs = {}
        if body:
            hdrs['Content-Type'] = "application/json"
        hdrs.update(headers)
        print "Fetch: %s %s" % (method, url)
        if body:
            print "Body: %s" % body
        print hdrs
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

class ChronosJob(object):
    fields = [
        "async",
        "command",
        "epsilon",
        "name",
        "owner",
        "disabled"
    ]

def connect(hostname, proto="http", username=None, password=None):
    return ChronosClient(hostname, proto="http", username=None, password=None)
