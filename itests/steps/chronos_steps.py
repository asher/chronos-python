import sys

import chronos
from behave import given, when, then

from itest_utils import get_chronos_connection_string

sys.path.append('../')


@given('a working chronos instance')
def working_chronos(context):
    """Adds a working chronos client as context.client for the purposes of
    interacting with it in the test."""
    if not hasattr(context, 'client'):
        chronos_connection_string = get_chronos_connection_string()
        context.client = chronos.connect(chronos_connection_string)


@when(u'we create a trivial chronos job')
def create_trivial_chronos_job(context):
    job = {
        'async': False,
        'command': 'echo 1',
        'epsilon': 'PT15M',
        'name': 'test_chronos_job',
        'owner': '',
        'disabled': True,
        'schedule': 'R/2014-01-01T00:00:00Z/PT60M',
    }
    context.client.add(job)


@then(u'we should be able to see it when we list jobs')
def list_chronos_jobs_has_trivial_job(context):
    jobs = context.client.list()
    job_names = [job['name'] for job in jobs]
    assert 'test_chronos_job' in job_names
