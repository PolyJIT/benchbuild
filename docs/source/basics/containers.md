# Containers

Benchbuild allows the definition of container images to define the base system
all experiment runs run in for a given project.

## Usage

If you want to run an experiment inside the project's container, simply replace
the usual ``run`` subcommand with the ``container run`` subcommand. Project and
experiment selection are done in the same way.

Example:
```
benchbuild container run -E raw linpack
```

This will run the following stages:

  1. Build all necessary base images.
     All images are initiated from a base image. Benchbuild knows how to construct
     a few base images. These will be prepared with all dependencies required to
     run benchbuild inside the container.
  2. Build all project images. Each project has to define its' own image.
  3. Build the experiment images. Each experiment can add anything it needs to the
     project images, if required. Use this to bring tools into the image that do
     not require any knowledge about the environment to run properly.
     For anything else, consider using a custom base image.

### Replace Images

Benchbuild will reuse any existing images it can find in your image registry.
The only relevant information is the image tag, e.g., ``benchbuild:alpine``.
If you want to avoid reuse and force to rebuild images unconditionally, you can
use the ``--replace`` flag when running the ``containers`` subcommand.

Example:
```
benchbuild container run --replace -E raw linpack
```

This will ignore **any** required image for the given experiments and projects.

## Configuration

You can configure the container environment using the following config variables.

- ``BB_CONTAINER_EXPORT``: Path where benchbuild stores exported container
  images. By default we store it in ``./containers/export``. Will be created
  automatically, if needed.
- ``BB_CONTAINER_IMPORT``: Path where to input images from into the registry.
  By default we load from ``./containers/export``.
- ``BB_CONTAINER_FROM_SOURCE``: Determine, if we should use benchbuild from the
  current source checkout, or from pip.
- ``BB_CONTAINER_ROOT``: Where we store our image layers. This is the image
  registry. Cannot be stored on filesystems that do not support subuid/-gid
  mapping, e.g. NFS.
  The default location is ``./containers/lib``.
- ``BB_CONTAINER_RUNROOT``: Where we store temporary image layers of running
  containers. See ``BB_CONTAINER_ROOT`` for restrictions.
  The default location is: ``./containers/run``.
- ``BB_CONTAINER_RUNTIME``: Podman can use any standard OCI-container runtime to
  launch containers. We use [crun](https://github.com/containers/crun) by
  default. Depending on your system, this one has already been installed with
  ``podman``.
  The default runtime is: ``/usr/bin/crun``
- ``BB_CONTAINER_MOUNTS``: A list of mountpoint definitions that should be added
  to all containers. With this you can add arbitrary tools into all containers.
  Default: ``[]``

## Definition

A project that wants to use a container image needs to define it in the
``CONTAINER`` attribute it using our declarative API provided by
``benchbuild.environments.domain.declarative``.

```
from benchbuild.environments.domain.declarative import ContainerImage

class Testproject(Project):
  CONTAINER = ContainerImage().from_('benchbuild:alpine')
```

The available set of commands follows the structure of a ``Dockerfile``.

## Runtime requirements

For containers to work properly, you need a few systems set up beforehand.

### Buildah

Image construction requires the [Buildah](https://buildah.io) tool. All image
construction tasks are formulated as buildah command calls in the backend.

Buildah is supported up to version 1.19.8.

### Podman

Container construction and execution is handed off to [Podman](https://podman.io).
Podman provides rootless containers and does not requires the execution of a
daemon process. However, you need to setup your user namespace properly to allow
mapping of subordinate uids/gids. Otherwise, podman will not be able to map
users other than the root user to filesystem permissions inside the container.

Please refer to podman's documentation on how to setup podman properly on your
system.

Podman is supported up to version 2.2.1

## Module: benchbuild.container

```{eval-rst}
.. automodule:: benchbuild.container
  :members:
  :undoc-members:
  :show-inheritance:
```

## Module: benchbuild.environments.domain.declarative

```{eval-rst}
.. automodule:: benchbuild.environments.domain.declarative
  :members:
  :undoc-members:
  :show-inheritance:
```

## Module: benchbuild.environments.domain.declarative

```{eval-rst}
.. automodule:: benchbuild.environments.domain.declarative
  :members:
  :undoc-members:
  :show-inheritance:
```

## Module: benchbuild.environments.domain.commands

```{eval-rst}
.. automodule:: benchbuild.environments.domain.commands
  :members:
  :undoc-members:
  :show-inheritance:
```
