# IJPP Journal

This experiment compares the following runtime configurations:
    * -O3 'naked' vs. JIT
    * -O3 'inside' vs. JIT
    * -O3 + Polly 'naked' vs. JIT
    * -O3 + Polly 'inside' vs. JIT

where 'naked' means without any JIT component involved, and 'inside' means
that the configuration will be executed inside the JIT pipeline, but
no PolyJIT-features are enabled.

## Configurations

## Evaluation

```eval_rst
.. automodule:: benchbuild.experiments.ijpp
    :members:
    :undoc-members:
    :show-inheritance:
```