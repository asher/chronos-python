from setuptools import setup


setup(
    name="chronos-python",
    version="1.2.0",
    author="Asher Feldman",
    author_email="asher@democument.com",
    description=("A Python client libary for the Chronos Job Scheduler."),
    license="MIT",
    keywords="chronos",
    packages=['chronos'],
    scripts=['bin/chronos-sync-jobs.py', 'bin/chronos-nagios.py'],
    long_description="A python client library for the Chronos Job Scheduler, with support scripts.",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=[
        'httplib2 >= 0.9'
    ],
    url='https://github.com/asher/chronos-python',
)
