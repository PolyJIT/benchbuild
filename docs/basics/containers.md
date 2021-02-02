Benchbuild allows the definition of container images to define the base system
all experiment runs run in for a given project.

## Usage

If you want to run an experiment inside the project's container, simply replace
the usual ``run`` subcommand with the ``container`` subcommand. Project and
experiment selection are done in the same way.

Example:
```
benchbuild container -E raw linpack
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

### Podman

Container construction and execution is handed off to [Podman](https://podman.io).
Podman provides rootless containers and does not requires the execution of a
daemon process. However, you need to setup your user namespace properly to allow
mapping of subordinate uids/gids. Otherwise, podman will not be able to map
users other than the root user to filesystem permissions inside the container.

Please refer to podman's documentation on how to setup podman properly on your
system.
