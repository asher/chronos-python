#!/usr/bin/env python
from __future__ import print_function

import errno
import os
import signal
import time
from functools import wraps

import requests


class TimeoutError(Exception):
    pass


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


@timeout(60)
def wait_for_chronos():
    """Blocks until chronos is up"""
    # we start chronos always on port 4400
    chronos_service = 'localhost:4400'
    while True:
        print('Connecting to chronos on %s' % chronos_service)
        try:
            response = requests.get('http://%s/ping' % chronos_service, timeout=2)
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ):
            time.sleep(2)
            continue
        if response.status_code == 200:
            print("Chronos is up and running!")
            break
