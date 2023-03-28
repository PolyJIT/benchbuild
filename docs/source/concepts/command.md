# Commands

BenchBuild provides an abstraction for binaries that are provided by a project,
after compilation. These ``Command`` objects carry the path to the binary,
customizable output paramters and support for dynamic tokens inside the path
generation.

Besides these features, a command behaves identical to any other binary
command that you make use of inside BenchBuild, e.g., ``benchbuild.utils.cmd``.

## Usage inside Projects

For now, you make use of BenchBuild's commands inside a project's ``WORKLOADS``
attribute. Let's have a look at the following example:

```
from benchbuild import Project
from benchbuild.command import Command, WorkloadSet, SourceRoot

class MyProject(Project):
  ...
  SOURCE = [
    Git(
      remote="https://github.com/myproject.git",
      local="myproject.git",
      limit=1,
      refspec="HEAD"
  ]

  WORKLOADS = {
    WorkloadSet("compression"): [
      Command(SourceRoot("myproject.git") / "myprj")
    ]
  }
```

Here we have a ``Command`` that belongs to the ``WorkloadSet`` with the name
``compression`` that points to the binary ``myprj`` inside the project's
source directory of the git source ``myproject.git``. What concrete path
this will be is only known after this project has been instanced inside
an experiment and is not known before.

This is done using tokens inside the commands' path representation. One
example of an available token is the above ``SourceRoot``.

## Tokens

BenchBuild offers project authors a way to tokenize path components for
commands. These can be used to refer to a project's root directory or
source directory in a generic way.
