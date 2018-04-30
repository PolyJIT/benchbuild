# Experiments

An experiment in benchbuild is a simple list of actions that need to be
executed on every project that is part of the experiment.
Every `callable` can serve as an action.

However, benchbuild provides many predefined actions that can
be reused by implementations in the `benchbuild.utils.actions` module.
Furthermore, if you do not need to control the default order of
actions for a run-time or a compile-time experiment you can reuse the
`Experiment.default_runtime_actions` or
`Experiment.default_compiletime_actions`.

Besides the list of actions, it is also the responsibility of an experiment
to configure each single project that should take part in an experiment.
This includes setting appropriate `CFLAGS`, `LDFLAGS` and any additional
metadata that has to be added to binary runs for later evaluation.

## The basic experiment

A basic experiment provides an override for the `actions_for_project` method and
a `NAME` attribute. If you want your experiment to perform actions on a project
you should return a list of actions from `actions_for_project`.

```python
import benchbuild.experiment as exp

class HelloExperiment(exp.Experiment):
    NAME = "hello-word"

    def actions_for_project(self, project):
        return []
```

## Default actions

As a shortcut, you can use the default implementations for run-time or compile-time experiments.
Consult ``benchbuild.utils.actions`` for all available actions.

```python
from benchbuild.experiment import Experiment

def actions_for_project(self, project):
    return Experiment.default_runtime_actions(project)
```

## Additional database schema

If your experiment requires additional tables in the database schema to store measurements, you can
add them to benchbuild's metadata and it will be created for you automatically. However, schema changes
are not versioned for your personal tables.

Full example:
```python
import benchbuild.utils.schema as schema
import benchbuild.experiment as exp
import sqlalchemy as sa

MYTABLE = sa.schema.Table('mytable', schema.metadata(), ...)

class MyExperiment(exp.Experiment)
    NAME = 'my-experiment'
    SCHEMA = [
        MYTABLE
    ]

    def actions_for_project(self, project):
        return exp.Experiment.default_runtime_actions(project)
```

Note that the ``SCHEMA`` attribute is not required for the tables to be created autoamtically. However, future
versions will use this to create a more targetted data dump.

## API reference

```eval_rst
.. autoclass:: benchbuild.experiment.Experiment
    :members:
    :undoc-members:
    :show-inheritance:
```
