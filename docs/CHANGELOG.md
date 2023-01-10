<a name="6.6.1"></a>
## 6.6.1 (2023-01-10)


#### Features

* **environments:**
  *  do not overwrite config, if cli option is default ([b1a095c1](https://github.com/PolyJIT/benchbuild/commit/b1a095c1e5b6ceb32b7eb3a7eda61918eeb3f757))
  *  improve error handling using result module ([fbb69502](https://github.com/PolyJIT/benchbuild/commit/fbb695027e83e99ab8dbbb58447bd3dc9d0073dd))
* **slurm:**  make container.runroot/container.root available for slurm customization ([616a4c69](https://github.com/PolyJIT/benchbuild/commit/616a4c69bea9ef17547cabfd2a8e076638b1e034), closes [#528](https://github.com/PolyJIT/benchbuild/issues/528))
* **source:**  make sure we manage the archive symlink properly. ([7687f0e3](https://github.com/PolyJIT/benchbuild/commit/7687f0e317b82b9e8a4b5e78a63827dd18255c06))
* **source/http:**  add auto-untar http source ([84f90e75](https://github.com/PolyJIT/benchbuild/commit/84f90e7568550a240a25c7cf06b139862f764ed0))

#### Bug Fixes

* **environments:**
  *  add missing logging import ([aad1b287](https://github.com/PolyJIT/benchbuild/commit/aad1b2878721c466167f52c176683d97d25a9f86))
  *  add missing Err import ([19c5983c](https://github.com/PolyJIT/benchbuild/commit/19c5983cd43e73d870212428bcc382d3e8255d9e))
  *  notify user when commit of container image fails ([78b890af](https://github.com/PolyJIT/benchbuild/commit/78b890af5fd03093bc74631bc6ac63c19477ee70))
* **project:**  version filters should only consider expandable sources ([3d546314](https://github.com/PolyJIT/benchbuild/commit/3d5463146debb66b3448acbf3ee79c4ef17ce35f))
* **source:**  enforce sorted order of revisions ([ca973ff0](https://github.com/PolyJIT/benchbuild/commit/ca973ff0b7e01e3b79b6daafdc7848e1433f766a))



## 6.5 (2022-11-03)

### Feat

- **source**: re-enable project_cls in enumerate_revision interface
- **versions**: enable context-aware SingleVersionFilter
- **source**: only print context-free sources
- **source**: expand public source API
- **source**: introduce type skeleton and prototypes for context-aware version enumeration.
- **action**: replace StepClass metaclass with __init_subclass__
- **actions**: mark StepTy covariant
- **actions**: use Stepable protocol as bound for StepTy.
- **actions**: accept any varargs in a Step's __call__ implementation

### Fix

- require dill version to be exactly 0.3.4
- linter warning
- linter warnings
- **project**: remove debug print
- **utils**: variant -> revision
- **tests**: repair tests after VariantContext replacement.
- **source**: remove runtime_checkable decorator
- **source**: use project class instead of object for enumerate
- **source**: return sequence of variants instead of nestedvariant
- **source**: clean up protocol apis
- **actions**: rename StepTy -> StepTy_co
- **tests**: remove notify_step_begin_end
- **actions**: reduce mypy errors
- **actions**: use mutable generic container

### Refactor

- **versions**: remove BaseVersionGroup
- **source**: replace VariantContext with Revision
- **source**: remove ExpandableAndFetchableSource from API

## 6.4 (2022-09-21)

### Feat

- **actions**: make MultiStep generic.
- **command**: make use of rendered and unrenderer PathToken explicit.
- **command**: safeguard pruning and backup
- **command**: add tests for enable_rollback
- **command**: add support for creates and consumes properties for commands
- **command**: add a label to commands
- **workload**: switch WorkloadSet to varargs instead of kwargs
- **command**: add example `OnlyIn` for WorkloadSet customization.

### Fix

- **command**: strictly less than python 3.9
- **command**: use _is_relative_to where needed
- **command**: guard is_relative_to with else
- **command**: do not depend on Path.is_relative_to (<python3.9)
- **command**: make mypy happy.
- **command**: Command.label is Optional
- **command**: use protocols instead of typing.Callable for callback functions
- **command**: Command.__getitem__ used constructor wrong
- **command**: return self._label instead of self.label
- **command**: return Path instead of str or PathToken
- **command**: assign consumed files to consumes attribute
- **tests**: remove missing_ok from unlink (python3.7)
- **tests**: repair test_command tests
- **tests**: make test project pickle'able
- **tests**: add missing pytest-git dependency
- **command**: `only` might be None
- **command**: access cache path instead of builddir path
- **command**: make sure SupportsUnwrap returns a WorkloadSet

### Refactor

- **command**: rename enable_rollback -> cleanup

## 6.3.2 (2022-08-21)

### Feat

- **command**: rename NullRenderer to RootRenderer
- **command**: hook up token renderer logic with Commands
- **command**: add support for generic path tokens
- **workload**: convert scimark2
- **command**: migrate git-based projects to workload sets
- **command**: add support for WorkloadSet.
- **command**: clear path tracker on fresh ProjectEnvironment
- **wrapping**: avoid wrapping the same command twice.
- **jobs**: add RunJob and RunJobs actions
- **command**: replace source root anywhere in command's parts
- **command**: pass environment to plumbum command
- **command**: pass args to plumbum command
- **command**: improve args and kwargs handling
- add env and __str__ to commands
- **command**: support declarative commands in projects (WIP)
- **source**: add 'fetch' support to FetchableSource derivatives
- **workloads**: add properties & tags accessors
- **workloads**: convert benchbuild.xz to support workloads

### Fix

- test must use render()
- **x264**: repair broken cli args
- **command**: actually run the workload
- **command**: check for existence, only after rendering
- **project**: target compile instead of run_tests, when accessing compile
- **command**: remove unused definitions
- **command**: context -> kwargs
- **typing**: python3.7 requires typing_extensions for runtime_checkable / Protocll
- **command**: missing rename job -> workload
- **command**: provide mapping type
- **workload**: strip previous workload draft
- workaround a mypy error
- correct mypy errors.
- **wrapping**: provide default arg for sprefix
- **actions**: provide default StepResult
- **command**: store args as tuple
- **bzip2**: clean draft marker
- **actions**: repair status print of actions
- **experiment**: initialize CleanExtra correctly
- **jobs**: allow jobs to run as wrapped binaries
- use oci_compliant name for image names
- **workloads**: wrong workload type
- **actions**: unbreak tests after list -> scalar conversion

### Refactor

- **command**: lower-case token str
- rename Job -> Workload
- **command**: remove debug prints
- **source**: remove unnecessary ellipsis

## 6.3.1 (2022-03-01)

### Feat

- **actions**: clean interfaces of utils/actions
- **workloads**: make object instance accessible to workloads using descriptors
- **workloads**: hook up Compile and Run action to new workload impl
- **workloads**: add simple intersection filter to workloads
- **workloads**: change workload registration decorator style.
- **workloads**: migrate Compile/Run action to run workloads only
- **project**: remove run_tests and compile abstract methods
- **gzip**: convert gzip to workloads
- **workload**: Add prototype support for workloads.
- **environments**: strip container args when entering interactive mode

### Fix

- **workloads**: typo.
- **gzip**: undo wrong wrap command
- **actions**: project -> obj after rebase

### Refactor

- **workloads**: remove useless/unused parts

## 6.3 (2022-02-03)

### Feat

- **actions**: throw error if RevisionStrings cannot match any Source.
- **source**: add FetchableSource.explore() method
- **source**: only filter context for expandable sources
- **actions**: support partial revisions in SetProjectVersion
- **source**: hook up context_from_revisions to SetProjectVersion
- **source**: provide an easy way to create a variant context
- **environments**: add container image removal to buildah adapter
- **environments**: support custom arguments in RunProjectContainer
- **actions**: track active_variant with SetProjectVersion
- **project**: add MultiVersioned Mixin to Projects
- **source**: symlink active version for http sources
- **source**: Link to active location after version()
- **actions**: Rename AddProjectVersion to SetProjectVersion
- **actions**: add AddProjectVersion action
- **actions**: remove obsolete parameters
- **actions**: remove attrs from utils/actions

### Fix

- **tests**: eye-breaking code alignment.
- **environments**: do not fail if no entrypoint is set.
- **environments**: supply args as dedicated subcommand args
- **environments**: use a default list factory, instead of a list class
- **source**: replace symlink to directory
- **actions**: obvious type errors in SetProjectVersion
- **actions**: assign active variant

### Refactor

- **pylint**: remove unused import
- **pylint**: make pylint happy.
- **pylint**: make pylint almost happy.

## 6.2.7 (2021-09-21)

## 6.2.6 (2021-09-16)

### Fix

- **sources**: do not use protocol class as ABC

## 6.2.5 (2021-09-15)

### Feat

- **utils/run**: add unbuffered watch commands
- **source**: update git remote revisions. (#434)
- **log**: add force_tty switch to control RichHandler. (#435)

## 6.2.4 (2021-09-03)

## 6.2.3 (2021-08-26)

### Fix

- **schema**: silence SAWarning about caching (#428)
- **environments**: pass format string to logging call (#427)

## 6.2.2 (2021-07-29)

## 6.2.1 (2021-07-06)

### Feat

- **environments**: add an interactive mode for container runs.

### Fix

- **logging**: make rich log to stderr by default (#415)
- **settings**: BB_ENV is ignored when no config file is loaded" (#414)

## 6.2 (2021-06-02)

### Fix

- **settings**: unbreak test cases.
- use correct schema version
- **settings**: consistent settings behavior.
- **environments**: notify the user, if image creation fails

## 6.1.1 (2021-05-11)

### Fix

- **project**: do not track project classes twice

## 6.1 (2021-05-11)

### Feat

- **environments**: just print env var name as error message
- **environments**: warn the user about too long paths for libpod
- **slurm**: support variable number of subcommand arguments
- tune down rich's custom log format
- **environments**: enable debugging of failed image builds
- **environments**: provide more consistent output through rich
- **environments**: add 'rmi' subcommand to delete images.
- **environments**: make an error message stand out more clearly
- **environments**: add g++ to base image
- **environments**: split image_exists into 2 implementations
- **environments**: split containers cli into 2 entitie
- **environments**: add basic error handling to environments
- **environments**: emit layer creation events
- **environments**: print layer construction progress
- **environments**: make layers hashable
- **environments**: step-wise image construction
- **environments**: split Repositories and Unit of Work into 2 entities each
- **utils/slurm**: add customizable SLURM templates
- **cli/project**: add details view for a single project
- **cli/project**: change project view to a condensed format
- **environments**: add option to replace container images
- add support for --export and --import flags in containers

### Fix

- **sources**: unshallow only when needed
- **environments**: unshallow git clones before dissociating
- **environments**: remove left-over parameters
- **ci**: typo.
- **environments**: do not overwrite exported images.
- **environments**: remove optional image name argument from podman load
- **slurm**: fix pylint/mypy
- **environments**: reuse same status bar structure for all other cli subcommands
- **environments**: mypy warnings
- **environments**: fix mypy/pylint annotations.
- **environments**: split return turple and baild out on error
- **environments**: mypy warnings
- **environments**: add missing type conversion
- **environments**: rework typing annotations for handlers
- **environments**: fix linter/mypy warnings
- **environments**: make Add & Copy layers hashable
- **environments**: add missing sys import
- **environments**: import Protocol from typing_extensions, if python <= 3.8
- **environments**: handle 'None' for MaybeContainer return type
- **slurm**: do not modify slurm_node_dir
- **environments**: deal with multi-line container ids
- **environments**: do not spawn the FromLayer
- **cli/project**: annotate print_layers
- **cli/project**: add neutral element for multiplication with reduce
- **project**: project registration for groups
- **environments**: explicitly state remote registry location
- do not use global state to conffigure buildah/podman
- **x264**: use local name of source for lookup

### Refactor

- **environments**: fix possible unbound variable
- **slurm**: fix type error on cli_process
- **environments**: remove unused sys import
- **environments**: rmeove some linter warnings
- **environments**: replace functools.partial with custom closure function
- **environments**: unsplit image from layer creation
- **enviroments**: remove debug print
- **environments**: remove unused commands
- **cli/project**: remove version counting from project view
- **cli/project**: force use of str
- **cli/project**: add documentation to print_project
- **cli/project**: add type annotation for set_limit
- **cli/project**: add a default list limit for versions (10)
- **cli/project**: provide better layout of project information
- **cli/project**: use a multi-line string
- **cli/project**: use named fields
- **project**: provide correct type annotations

## 6.0.1 (2020-12-29)

### Fix

- Avoid useless plugin spam when running with higher verbosity levels
