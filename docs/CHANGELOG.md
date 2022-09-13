## 6.3.2 (2022-08-21)

### Feat

- **source**: add 'fetch' support to FetchableSource derivatives

### Fix

- use oci_compliant name for image names

### Refactor

- **source**: remove unnecessary ellipsis

## 6.3.1 (2022-03-01)

### Feat

- **environments**: strip container args when entering interactive mode

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
