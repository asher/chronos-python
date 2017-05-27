#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2014 Asher Feldman
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

import os
import sys
import re
import argparse
import json
import logging
import chronos


def read_job_file(path):
    f = open(path, "r")
    try:
        job = json.loads(f.read())
        if "name" in job:
            return job
    except:
        print "Error: failed to decode %s" % path


def find_json_files(path):
    """find /path -name *.json"""
    job_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if re.search(r"json$", file):
                job_files.append(root + '/' + file)
    return sorted(job_files)


def check_update(jobs, job):
    """Return True if the job definition on Chronos != local json config"""
    on_chronos = jobs[job['name']]
    for key in job.keys():
        if key in on_chronos:
            if on_chronos[key] != job[key]:
                return True
        else:
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Tool for syncing Chronos jobs from local .json files")
    parser.add_argument("--hostname", metavar="<host:port>", required=True,
                        help="hostname and port of the Chronos instance")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sync", metavar="/path/to/dir",
                       help="path to a directory containing json files describing chronos jobs. \
                       All sub-directories will be searched for files ending in .json")
    group.add_argument("--list", action="store_true", help="list jobs on chronos")
    parser.add_argument("-n", action="store_true", default=False,
                        help="dry-run, don't actually push anything to chronos")
    args = parser.parse_args()

    c = chronos.connect(args.hostname)
    cjobs = c.list()

    if args.list:
        # cjobs isn't json but this still gets us the pretty
        print json.dumps(cjobs, sort_keys=True, indent=4)
        sys.exit(0)

    if args.sync:
        jobs = {}
        retry = {'update': [], 'add': []}
        for job in cjobs:
            jobs[job["name"]] = job

        if not os.path.isdir(args.sync):
            raise Exception("%s must be a directory" % args.sync)

        job_files = find_json_files(args.sync)
        for file in job_files:
            job = read_job_file(file)
            if not job:
                print "Skipping %s" % file
            else:
                if job['name'] in jobs:
                    if check_update(jobs, job):
                        print "Updating job %s from file %s" % (job['name'], file)
                        if not args.n:
                            try:
                                c.update(job)
                            except:
                                retry['update'].append(job)
                    else:
                        print "Job %s defined in %s is up-to-date on Chronos" \
                            % (job['name'], file)
                else:
                    print "Adding job %s from file %s" % (job['name'], file)
                    if not args.n:
                        try:
                            c.add(job)
                        except:
                            retry['add'].append(job)

        attempt = 0
        while (len(retry['update']) > 0 or len(retry['add']) > 0) and attempt < 10:
            attempt += 1
            if len(retry['update']) > 0:
                job = retry['update'].pop(0)
                try:
                    print "Retry %d for job %s" % (attempt, job['name'])
                    c.update(job)
                except:
                    retry['update'].append(job)

            if len(retry['add']) > 0:
                job = retry['add'].pop(0)
                try:
                    print "Retry %d for job %s" % (attempt, job['name'])
                    c.add(job)
                except:
                    retry['add'].append(job)

        if len(retry['update']) > 0 or len(retry['add']) > 0:
            print "Failed Jobs: %s" % sorted((retry['update'] + retry['add']))


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level="WARN")
    main()
