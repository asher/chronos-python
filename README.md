chronos-python
==============

Simple python api for the chronos job scheduler

###Installation

    python setup.py install

###Usage Example

```
import chronos
c = chronos.connect("chronos.mesos.server.com:8080")

# get list of scheduled jobs and their status as
# [{ 'name': 'job1', ..}, { 'name': 'job2', ..}]
jobs = c.list()

# run job by name
c.run("job123")

# add || update
job = { 'async': False, 'command': 'echo 1', 'epsilon': 'PT15M', 'name': 'foo',
    'owner': 'me@foo.com', 'disabled': True, 'schedule': 'R/2014-01-01T00:00:00Z/PT60M'}
try:
    c.add(job) # fails if job of the same name already exists
except:
    c.update(job)

# delete job by name
c.delete("job123")

# kill all tasks for a running/stuck job
c.delete_tasks("job123")
```


###Included Scripts
* `chronos-sync-jobs.py` - Sync chronos jobs from a directory tree containing job.json files.
`chronos-sync-jobs.py --hostname --hostname chronos.server.com:4400 --sync /path/to/job.json/files`
