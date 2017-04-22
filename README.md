# chronos-python

[![Build Status](https://travis-ci.org/asher/chronos-python.svg?branch=master)](https://travis-ci.org/asher/chronos-python)

This is a Python client library for the [Chronos](https://mesos.github.io/chronos/docs/api.html) HTTP [Rest API](https://mesos.github.io/chronos/docs/api.html)

## Installation

    pip install chronos-python
    # or
    git clone git@github.com/asher/chronos-python
    python setup.py install

## Usage Examples


Create a ``ChronosClient``

    >>> import chronos
    >>> client = chronos.connect("chronos.mesos.server.com:8080")
    # or specify multilple servers that will be tried in order
    >>> client = chronos.connect(["chronos1.mesos.server.com:8080", "chronos2.mesos.server.com:8080"])

List all jobs:

     >>> client.list()
     [{u'softError': False, u'scheduleTimeZone': u'null', u'successCount': 702, u'cpus': 0.25, u'disabled': False, u'ownerName': u'', u'owner': u'noop', u'disk': 256.0, u'errorCount': 0, u'container': {u'image': u'my-docker-registry:443/myimage', u'type': u'docker', u'network': u'BRIDGE', u'volumes': []}, u'errorsSinceLastSuccess': 0, u'highPriority': False, u'dataProcessingJobType': False, u'arguments': [], u'uris': [u'file:///root/.dockercfg'], u'shell': True, u'description': u'', u'schedule': u'R/2015-12-18T10:40:00.000Z/PT10M', u'mem': 1024.0, u'epsilon': u'PT60S', u'retries': 2, u'name': u'my job 1', u'runAsUser': u'root', u'lastSuccess': u'2015-12-18T10:30:09.755Z', u'environmentVariables': [], u'executorFlags': u'', u'command': u'sensu-scheduled-canary.sh', u'executor': u'', u'async': False, u'lastError': u'', u'constraints': []}, {u'softError': False, u'scheduleTimeZone': u'null', u'successCount': 40, u'cpus': 0.25, u'disabled': False, u'ownerName': u'', u'owner': u'noop', u'disk': 256.0, u'errorCount': 0, u'container': {u'image': u'my-docker-regsitry:443/myimage', u'type': u'docker', u'network': u'BRIDGE', u'volumes': [], u'errorsSinceLastSuccess': 0, u'highPriority': False, u'dataProcessingJobType': False, u'arguments': [], u'uris': [u'file:///root/.dockercfg'], u'shell': True, u'description': u'', u'schedule': u'R/2015-12-18T11:00:00.000Z/PT60M', u'mem': 1024.0, u'epsilon': u'PT60S', u'retries': 2, u'name': u'example_service mesosstage_kwabatch gitfb0c7ac5 config95bc9b2f', u'runAsUser': u'root', u'lastSuccess': u'2015-12-18T08:00:12.965Z', u'environmentVariables': [], u'executorFlags': u'', u'command': u'echo "This batch should run once per hour, and take 2 hours" && sleep 2h', u'executor': u'', u'async': False, u'lastError': u'', u'constraints': []}]


Add a new job:

    >>> job = { 'async': False, 'command': 'echo 1', 'epsilon': 'PT15M', 'name': 'foo',
    'owner': 'me@foo.com', 'disabled': True, 'schedule': 'R/2014-01-01T00:00:00Z/PT60M'}
    >>> client.add(job)

Update an existing job:

    >>> job = { 'async': False, 'command': 'echo 1', 'epsilon': 'PT15M', 'name': 'foo',
    'owner': 'me@foo.com', 'disabled': True, 'schedule': 'R/2014-01-01T00:00:00Z/PT60M'}
    >>> client.update(job)

Run a job:

    >>> client.run("job123")

Delete a job:

    >>> client.delete("job123")

Delete all the in flight tasks for a job:


    >>> client.delete_tasks("job123")


## Included Scripts
* `chronos-sync-jobs.py` - Sync chronos jobs from a directory tree containing job.json files.
`chronos-sync-jobs.py --hostname chronos.server.com:4400 --sync /path/to/job.json/files`

* `chronos-nagios.py` - Nagios/Icinga style monitor of jobs
`chronos-nagios.py --hostname chronos.server.com:4400 --crit 3 --prefix etl. --prefix data.`
`chronos-nagios.py --hostname chronos.server.com:4400 --crit 3 --exclude etl.`

## Testing

``chronos-python`` uses Travis to test against multiple versions of Chronos. You can run the tests locally on any machine
with [Docker](https://www.docker.com/) and [Docker compose](https://docs.docker.com/compose/) on it.

To run the tests:

    make itests

To run against a different version of Chronos:

    CHRONOSVERSION=3.0.2 make itests
