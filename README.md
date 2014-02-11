chronos-python
==============

Simple python api for the chronos job scheduler

###Installation

    python setup.py install

###Usage Example

```
import chronos
c = chronos.connect("chronos.mesos.server.com")

# list jobs
jobs = c.list()

# run job
c.run("job123")

# add || update
job = { 'async': False, 'command': 'echo 1', 'epsilon': 'PT15M', 'name': 'foo',
    'owner': 'me@foo.com', 'disabled': True, 'schedule': 'R/2014-01-01T00:00:00Z/PT60M'}
try:
    c.add(job)
except:
    c.update(job)
```

