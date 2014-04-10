import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "chronos-python",
    version = "0.31",
    author = "Asher Feldman",
    author_email = "asher@democument.com",
    description = ("A Python client libary for the Chronos Job Scheduler."),
    license = "MIT",
    keywords = "chronos",
    packages=['chronos'],
    scripts=['bin/chronos-sync-jobs.py', 'bin/chronos-nagios.py'],
    long_description="A python client library for the Chronos Job Scheduler, with support scripts.",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
    ],
)
