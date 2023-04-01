# Actions

Actions are used to declare the workflow of an experiment. BenchBuild provides
a set of default actions that should suit most experiments.
A new experiment can define a new set of actions that should be used per project,
or use those defaults.

## Customize actions

Whenever you define a new expeirment, you have to provide an implementation
for ``def actions_for_project(self, project: 'Project')``.
This implementation usually configures extensions on the project and returns
a set of actions that should be run during execution.

Example:
```{python}
def actions_for_project(self, project: 'Project'):
  project.runtime_extension = time.RunWithTime(
    run.RuntimeExtensions(project, self))
  project.runtime_extension = time.WithTimeout(
    run.RunCompiler(project, self))

  return self.default_runtime_actions(project)
```

This takes care of compiling, running and cleanup during experiment execution.

## Available Actions

The following actions are available out of the box. You can define your own
actions at any time

### Step (Base)

### Clean

### MakeBuildDir

### Compile

### Run

### Echo

### Any (Group)

### Experiment (Any, Group)

### RequireAll (Group)

### CleanExtra

### ProjectEnvironment

### SetProjectVersion

This action provides you with a way to change the source version used inside the
build directory of this project.
During initialization, each project is assigned a variant that determines the
source versions that will be checked out into the build directory.

Sometimes it can be useful to do comparisons of different source revisions
inside a single experiment run. This can be achieved using ``SetProjectVersion``.

Usage:
```{python}
from benchbuild.source.base import RevisionStr
from benchbuild.utils import actions as a

...
git_commit_hash = 'abcdefgh'

actions = [
  a.Clean(project),
  a.MakeBuildDir(project),
  # This uses the default variant of the project (not necessarily 'abcdefgh')
  a.ProjectEnvironment(project),
  a.Compile(project),
  a.Run(project),

  # From here we will work with git sources set to 'abcdefgh'
  a.SetProjectVersion(project, RevisionStr(git_commit_hash))
  a.Compile(project),
  a.Run(project)
]
```

The match is done on all(!) sources of the project. If you happen to find a
revision string twice in different souces, both will be checked out in the
build directory.

The match is done exact and matches agains the ``source.versions()`` output of a
source. Only sources that are marked as expandable (``source.is_expandable``)
will be checked.

```{eval-rst}
.. automodule:: benchbuild.utils.actions
  :members:
  :undoc-members:
  :show-inheritance:
```
