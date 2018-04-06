# Projects

A project in benchbuild is an abstract representation of a software system that can live in various stages throughout an experiment.
It defines two extension points for an experiment to attach on, the compile-time phase and the (optional) run-time phase.

An experiment can intercept the compilation phase of a project and perform any experiment that requires the source artifacts as input.
Furthermore, it is possible to intercept a project's run-time pahse with a measurement.

The project definition ensures that all experiments run through the same series of commands in both phases and that all experiments run inside a separate build directory in isolation of one another.

## Phases
As introduced, the main focus of a project lies on two phases.

1. Compilation: Any custom extension set to a project's `compiler_extension` property will be run in this phase.
2. Runtime: Any custom extension set to a project's `runtime_extension` property will be run in this pahse.

## Minimal Example
Let us have a look at a minimal example for a simple new project ``HelloWorld`` written in C.
First, we start with the minimal structure of a project.
```python
import benchbuild.project as p
class HelloWorld(p.Project):
    NAME = "HelloWorld"
    DOMAIN = "Example"
    GROUP = "ExampleGroup"
    SRC_FILE = "hi.c"

    def download(self):
        pass

    def configure(self):
        pass

    def build(self):
        pass
```

Here we only provide a skeleton without any implementation, so this project can be recognized by benchbuild but not do anything useful, yet.
``HelloWorld``'s python package needs to be registered to benchbuild settings under the section: ``plugins -> projects``.
However, our project lacks any implementation details about wrapping a compiler and a binary, so we won't be able to do anything useful with it.

### Wrapping the Compiler

### Wrapping a Binary

## API Reference

```eval_rst
.. autoclass:: benchbuild.project.Project
    :members:
    :undoc-members:
    :show-inheritance:
```
