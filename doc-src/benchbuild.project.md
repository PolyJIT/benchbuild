# Projects

A project in Benchbuild is an abstract representation of a software system that can live in various stages throughout an experiment.
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

Historically, Benchbuild was focussed on interaction with the LLVM toolchain and namely the C/C++ frontend clang/clang++, hence the naming of the following wrapper functions.
If you want to wrap the compiler at any stage of a project's phases you can use the methods ``lt_clang`` for a C compiler and ``lt_clang_cxx`` for a C++ compiler included in the module
``benchbuild.utils.compiler``.

The wrapper will provide you with a callable that runs the compiler (which is now substituted
with a script that runs the compiler (without flags) and our compiler extension.
Our project ``CFLAGS`` and ``LDFLAGS`` are hidden inside the wrapper and appended to the compiler command line autoamtically.

```python
from benchbuild.project import Project
from benchbuild.utils.compiler import lt_clang

class MyProject(Project):
    NAME = 'MyProject'
    DOMAIN = 'myprojects'
    GROUP = 'myprojects'
    VERSION = '1.0.0'
    SRC_FILE = 'myproject.c'

    ...

    def build(self):
        clang = lt_clang(self.cflags, self.ldflags, self.compiler_extension)
        clang("-O3", "-o", "myproject", SRC_FILE)
```


### Wrapping a Binary

In addition to compilers we can also wrap arbitrary binaries with our runtime extension using the ``benchbuild.utils.wrapping``.
For example, if we want to wrap the ``myproject`` binary from the previous example, we would proceed
as follows:

```python
from benchbuild.utils.wrapping import wrap

def run_tests(self, experiment, runner):
    wrapped = wrap("myproject", experiment)
    runner(wrapped['--verbose', '--myflag'])
```

Note, that you can add arbitrary flags to the wrapped binary, e.g., ``--verbose`` and ``--myflag``.
The ``run_tests`` method of ``project`` provides 2 parameters.
First, the composed run-time extension ``experiment``, which was configured by the experiment.
Second, a ``runner``, which provides a unified way for benchbuild to control the output and execution
of the wrapped binary.
You should use it for all executions performed in ``run_tests``, but nothing will break horribly if you don't.


## API Reference

```eval_rst
.. autoclass:: benchbuild.project.Project
    :members:
    :undoc-members:
    :show-inheritance:
```
