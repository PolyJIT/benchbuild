# Installation

The installation instructions are tested against Ubuntu 20.04 for Python 3.7 and Python 3.8. The particular commands required for installation depend on your setup.
The dependencies below are not always mandatory, if they are not used.

## Requirements

Dependency   | Minimum Version | Notes
-------------|-----------------|----------------------------
Python       | 3.7             |
libpq        | 9.6             | Required by psycopg2.
libfuse      | 2.9.9           | If uchroot is used.
unionfs-fuse | 1.0             | If unionfs support is used.
slurm-llnl   | 18.08           | If slurm support is used.


### PostgreSQL

The library dependency ``libpq`` is always need right now, because we make use of psycopg2 features internally. It is planned to get rid of this dependency in the future.
### FUSE

BenchBuild can make use of ``unionfs`` and ``libfuse``. This is often used in conjunction with a tool named ``uchroot`` which provides legacy support for user-space containers.
This will be obsolete as soon as ``podman``/``buildah`` based OCI container support is considered stable.

### SLURM

The cluster management software ``slurm`` is only required by 'name', i.e., we have to be able to import the binaries as python objects in benchbuild. As an alternative to installing ``slurm`` on your machine, you can always provide symlinks to ``/bin/true`` to the commands ``sbatch`` and ``srun``.

The minimum version should signal the minimum features set expected by BenchBuild when generating a ``slurm`` batch script.

## Benchbuild

BenchBuild is released via pip and can be installed on your system as follows:

``` bash
pip install benchbuild
```

If you want to isolate BenchBuild from the rest of your system packages, you can install it in a dedicated virtual environment.

``` bash
virtualenv -ppython3 <venv_path>
source <venv_path>/bin/activate
pip3 install benchbuild
```

### Bootstrapping

BenchBuild provides a bootstrap procedure that checks a few key binaries on your system and tries to assist you in installation of any necessary binaries.
