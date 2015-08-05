import time

from itest_utils import wait_for_chronos


def before_all(context):
    wait_for_chronos()


def after_scenario(context, scenario):
    """If a chronos client object exists in our context, delete any jobs before the next scenario."""
    if context.client:
        while True:
            jobs = context.client.list()
            if not jobs:
                break
            for job in jobs:
                context.client.delete(job['name'])
            time.sleep(0.5)
