import csv
import logging
import sys
from behave import given, when, then
import time
import os

import chronos

log = logging.getLogger('chronos')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)
CHRONOSVERSION = os.getenv('CHRONOSVERSION', '3.0.2')
LEGACY_VERSIONS = ('2.4.0',)


@given('a working chronos instance')
def working_chronos(context):
    """Adds a working chronos client as context.client for the purposes of
    interacting with it in the test."""
    if not hasattr(context, 'client'):
        chronos_servers = ['127.0.0.1:4400']
        if CHRONOSVERSION in LEGACY_VERSIONS:
            scheduler_version = None
        else:
            scheduler_version = 'v1'
        context.client = chronos.connect(chronos_servers, scheduler_version=scheduler_version)


@when(u'we create a trivial chronos job named "{job_name}"')
def create_trivial_chronos_job(context, job_name):
    job = {
        'command': 'echo 1',
        'name': job_name,
        'owner': '',
        'disabled': False,
        'schedule': 'R0/2014-01-01T00:00:00Z/PT60M',
    }
    if CHRONOSVERSION in LEGACY_VERSIONS:
        job['async'] = False
    try:
        context.client.add(job)
        context.created = True
    except:
        context.created = False
    # give it a bit of time to reflect the job in ZK
    time.sleep(0.5)


@then(u'we should be able to see the job named "{job_name}" when we list jobs')
def list_chronos_jobs_has_trivial_job(context, job_name):
    jobs = context.client.list()
    job_names = [job['name'] for job in jobs]
    assert job_name in job_names


@then(u'we should not see the job named "{job_name}" when we list jobs')
def list_chronos_jobs_hasnt_trivial_job(context, job_name):
    jobs = context.client.list()
    job_names = [job['name'] for job in jobs]
    assert job_name not in job_names


@then(u'we should be able to delete the job named "{job_name}"')
def delete_job_with_spaces(context, job_name):
    context.client.delete(job_name)
    time.sleep(0.5)


@then(u'we should not be able to see the job named "{job_name}" when we list jobs')
def not_see_job_with_spaces(context, job_name):
    jobs = context.client.list()
    job_names = [job['name'] for job in jobs]
    assert 'test chronos job with spaces' not in job_names

@then(u'we should be able to see {num_jobs:d} jobs in the job graph')
def see_job_in_graph(context, num_jobs):
    jobs = csv.reader(context.client.scheduler_graph().splitlines())
    actual = sum(1 for row in jobs)
    assert actual == num_jobs


@then(u'we should be able to see timings for the job named "{job_name}" when we look at scheduler stats')
def check_job_has_timings(context, job_name):
    stats = context.client.job_stat(job_name)
    assert stats == {'histogram': {
        'median': 0.0,
        '98thPercentile': 0.0,
        '75thPercentile': 0.0,
        '95thPercentile': 0.0,
        '99thPercentile': 0.0,
        'count': 0,
        'mean': 0.0,
        },
        'taskStatHistory': []
    }


@then(u'we should be able to see percentiles for all jobs')
def check_percentiles(context):
    ninety_ninth = context.client.scheduler_stat_99th()
    ninety_eighth = context.client.scheduler_stat_98th()
    ninety_fifth = context.client.scheduler_stat_95th()
    seventy_fifth = context.client.scheduler_stat_75th()
    for percentile in ninety_ninth, ninety_eighth, ninety_fifth, seventy_fifth:
        assert percentile == [{'jobNameLabel': 'myjob', 'time': 0.0}]


@then(u'we should be able to see the median timing for all jobs')
def check_median(context):
    medians = context.client.scheduler_stat_median()
    assert medians == [{'jobNameLabel': 'myjob', 'time': 0.0}]


@then(u'we should be able to see the mean timing for all jobs')
def check_mode(context):
    modes = context.client.scheduler_stat_median()
    assert modes == [{'jobNameLabel': 'myjob', 'time': 0.0}]

@then(u'we should be able to see metrics')
def check_metrics(context):
    metrics = context.client.metrics()
    assert isinstance(metrics, dict)
    assert metrics.has_key("version")
    assert metrics.has_key("gauges")
