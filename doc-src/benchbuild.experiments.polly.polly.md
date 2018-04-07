# Polly (Default)

This experiment applies polly's transformations to all projects and measures
the runtime.

## Configurations

All projects are configured to apply Polly without any other configuration options.
So this will just add `-polly -O3` to the CFLAGS of each project.

## Evaluation

* time.user_s - The time spent in user space in seconds (aka virtual time)
* time.system_s - The time spent in kernel space in seconds (aka system time)
* time.real_s - The time spent overall in seconds (aka Wall clock)

You can use the `raw` report for evaluation.

## API reference

```eval_rst
.. automodule:: benchbuild.experiments.polly.polly
    :members:
    :undoc-members:
    :show-inheritance:
```