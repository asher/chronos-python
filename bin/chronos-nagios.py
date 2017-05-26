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

import sys
import re
import argparse
import logging
import chronos


def match_prefix(prefixes=[], job=''):
    for prefix in prefixes:
        if re.search('^' + prefix, job):
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Monitor the status of Chronos Jobs")
    parser.add_argument("--hostname", metavar="<host:port>", required=True,
                        help="hostname and port of the Chronos instance")
    parser.add_argument("--prefix", metavar="job-prefix", required=False, action="append",
                        help="if set, only check jobs matching this prefix")
    parser.add_argument("--exclude", metavar="job-prefix", required=False, action="append",
                        help="if set, exclude jobs matching this prefix")
    parser.add_argument("--warn", metavar="#", default=1,
                        help="warn if at least this number of jobs are currently failed")
    parser.add_argument("--crit", metavar="#", default=1,
                        help="critical if at least this number of jobs are currently failed")
    args = parser.parse_args()

    fails = []
    ok = []
    unknown = []

    c = chronos.connect(args.hostname)
    cjobs = c.list()

    if not isinstance(cjobs, list):
        print "UNKNOWN: error querying chronos"
        sys.exit(3)

    for job in cjobs:
        if job['disabled']:
            continue

        if isinstance(args.prefix, list):
            if not match_prefix(args.prefix, job['name']):
                continue

        if isinstance(args.exclude, list):
            if match_prefix(args.exclude, job['name']):
                continue

        if job['lastError'] > job['lastSuccess']:
            fails.append(job['name'].encode('ascii'))
        elif job['lastSuccess']:
            ok.append(job['name'].encode('ascii'))
        else:
            unknown.append(job['name'].encode('ascii'))

    if len(unknown) > 0:
        umsg = "(%d waiting for execution or with no data)" % len(unknown)
    else:
        umsg = ''

    if len(fails) == 0:
        print "OK: %d jobs succeeded on last run %s" % (len(ok), umsg)
        sys.exit(0)
    elif len(fails) >= int(args.crit):
        print "CRITICAL: %d failed jobs: %s %s" % (len(fails), str(fails).strip('[]'), umsg)
        sys.exit(2)
    elif len(fails) >= int(args.warn):
        print "WARNING: %d failed jobs: %s %s" % (len(fails), str(fails).strip('[]'), umsg)
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level="WARN")
    main()
