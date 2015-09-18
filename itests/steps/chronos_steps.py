import sys
import logging
import chronos
from behave import given, when, then

from itest_utils import get_chronos_connection_string

sys.path.append('../')

log = logging.getLogger('chronos')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)


@given('a working chronos instance')
def working_chronos(context):
    """Adds a working chronos client as context.client for the purposes of
    interacting with it in the test."""
    if not hasattr(context, 'client'):
        chronos_connection_string = get_chronos_connection_string()
        context.client = chronos.connect(chronos_connection_string)


@when(u'we create a trivial chronos job named "{job_name}"')
def create_trivial_chronos_job(context, job_name):
    job = {
        'async': False,
        'command': 'echo 1',
        'epsilon': 'PT1M',
        'name': job_name,
        'owner': '',
        'disabled': False,
        'schedule': 'R/2014-01-01T00:00:00Z/PT60M',
    }
    context.client.add(job)


@then(u'we should be able to see the job named "{job_name}" when we list jobs')
def list_chronos_jobs_has_trivial_job(context, job_name):
    jobs = context.client.list()
    job_names = [job['name'] for job in jobs]
    assert job_name in job_names


@then(u'we should be able to delete the job named "{job_name}"')
def delete_job_with_spaces(context, job_name):
    context.client.delete(job_name)


@then(u'we should not be able to see the job named "{job_name}" when we list jobs')
def not_see_job_with_spaces(context, job_name):
    jobs = context.client.list()
    job_names = [job['name'] for job in jobs]
    assert 'test chronos job with spaces' not in job_names


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
