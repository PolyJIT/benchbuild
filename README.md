# BenchBuild: Empirical-Research Toolkit
![Python CI](https://github.com/PolyJIT/benchbuild/workflows/Python%20CI/badge.svg)
![Build Documentation](https://github.com/PolyJIT/benchbuild/workflows/Build%20Documentation/badge.svg)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/217af919753b4d16b3760282c1274751)](https://www.codacy.com/app/polyjit/benchbuild_2?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=PolyJIT/benchbuild&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/PolyJIT/benchbuild/branch/master/graph/badge.svg)](https://codecov.io/gh/PolyJIT/benchbuild)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

BenchBuild provides a lightweight toolkit to conduct empirical compile-time and run-time experiments.
Striving to automate all tedious and error-prone tasks, it downloads, configure and builds all supported projects fully automatic and provides tools to wrap the compiler and any resulting binary with a customized measurement.

All results can be stored as the user desires.
BenchBuild tracks the execution status of all its managed projects inside an own database.

## Features

- Wrap compilation commands with arbitrary measurement functions written in python.
- Wrap binary commands with arbitrary measurement functions written in python.
- Parallel benchmarking using the SLURM cluster manager.

## Installation

BenchBuild is available via PyPI. You can install the latest release with pip.
```bash
# Global install
$ pip install benchbuild
# Lokal install
$ pip install --user benchbuild
# Recommended: Install into a virutalenv.
$ virtualenv benchbuild
...
$ source benchbuild/bin/activate
...
$ pip install benchbuild
```

After installation you can start using benchbuild with the frontend `benchbuild`.
Without arguments, you will be greeted with the following help output:
```bash
benchbuild 3.3.1.dev1+gf43b2d0

Frontend for running/building the benchbuild study framework.

Usage:
    benchbuild [SWITCHES] [SUBCOMMAND [SWITCHES]] args...

Meta-switches:
    -h, --help      Prints this help message and quits
    --help-all      Print help messages of all subcommands and quit
    --version       Prints the program's version and quits

Switches:
    -d              Enable debugging output
    -v              Enable verbose output; may be given multiple times

Subcommands:
    bootstrap       Bootstrap benchbuild external dependencies, if possible.; see 'benchbuild bootstrap --help' for more info
    config          Manage BenchBuild's configuration.; see 'benchbuild config --help' for more info
    experiment      Manage BenchBuild's known experiments.; see 'benchbuild experiment --help' for more info
    log             Frontend command to the benchbuild database. ; see 'benchbuild log --help' for more info
    project         Manage BenchBuild's known projects.; see 'benchbuild project --help' for more info
    report          Generate Reports from the benchbuild db.; see 'benchbuild report --help' for more info
    run             Frontend for running experiments in the benchbuild study framework.; see 'benchbuild run --help' for more info
    slurm           Generate a SLURM script. ; see 'benchbuild slurm --help' for more info
```

You can now start using benchbuild. However, you might want to configure benchbuild to your needs. Therefore, it is recommended to generate a default configuration first.
```bash
$ benchbuild config write
```

This will place a .benchbuild.yml in the current directory, containing all default values for
your system. You can modify the configuration as you wish, most of the configuration options
are explained with a description in the config file.

### Important configuration options

The following configuration options are considered to be very important for benchbuild's behavior.
```
build_dir (BB_BUILD_DIR):
  All generated artifacts will be placed in this directory. By default, it will be cleaned
  at the end of an experiment.

db (BB_DB_*):
  connect_str (BB_DB_CONNECT_STR):
    You need to place a valid sqlalchemy connect string here. It will be used to establish a
    database connection.
    By default an in-memory SQLite database is used (sqlite:///).

env (BB_ENV_*):
  ld_library_path (BB_LD_LIBRARY_PATH):
    Modify benchbuild's LD_LIBRARY_PATH variable. You can use this to provide access to
    libraries outside of the system's default library search path.
  path (BB_PATH):
    Modify benchbuild's PATH variable. You can use this to provide access to
    binaries outside of the system's default binary search path.
  home (BB_HOME):
    Modify benchbuild's HOME variable. You can use this to set a custom home
    directory, if the default home is not available to benchbuild.

test_dir (BB_TEST_DIR):
  Some distributed projects require additional test-inputs that are too big for
  distribution with benchbuild. Therefore, there exists an additional repository (private)
  that contains the input files for these projects. Please contact the authors for access
  to this repository, if you need run-time tests with these projects.

tmp_dir (BB_TMP_DIR):
  BenchBuild will download the source code for all projects into this directory. We avoid
  repeated downloads by caching them here. This directory won't be cleaned and all downloads
  are hashed. If you want to re-download the source, just delete the hash file (or the source file).

unionfs (BB_UNIONFS_*):
  unionfs_enable: (BB_UNIONFS_ENABLE):
    Enable/Disable unionfs features. By default unionfs is switched off. If you enable unionfs,
    all projects will be wrapped in two layers: One read-only layer containing the prepared
    source files and one writeable layer. This way you can easily run different configurations
    without wiping the build-directory completely. As this requires additional setup, it is
    not recommended to be switched on by default.
```

## Database

BenchBuild stores results/maintenance data about your experiments inside a database.
While a sqlite3 in-memory database is used by default, you might want to provide a more permanent solution to keep your experiment data persistent.

### PostgreSQL

The preferred way is using a more sophisticated DBMS such as PostgreSQL.
If you are using features like SLURM, make sure that your DBMS is reachable from all nodes that might run benchbuild.

Setup your postgres cluster with a user and a database for benchbuild to use.

```sql
CREATE USER benchbuild;
CREATE DATABASE benchbuild;
```

In the configuration you supply the complete connect-string in sqlalchemy's format, e.g.: `postgresql+psycopg2://benchbuild:benchbuild@localhost:5432/benchbuild`

```yaml
# .benchbuild.yml
db:
  connect_string:
    default: sqlite://
    value:  postgresql+psycopg2://benchbuild:benchbuild@localhost:5432/benchbuild
```

### SQLite

As mentioned, by default we use an in-memory sqlite database. You can persist this one for your local usage, by supplying a filename in the database configuration.

```yaml
# .benchbuild.yml
db:
  connect_string:
    default: sqlite://
    value:  sqlite:////absolute/path/to/sqlite.db
```

## Advanced Features

Advanced features require additional packages on your system.

### UnionFS

We can maintain UnionFS mounts for uchroot-based projects, such as all Gentoo derived projects.
This avoids continuous unpacking of the container-filesystem and keeps one unpacked version as
a read-only layer at the bottom of the filesystem-stack.

You need to configure subuid/subgid ranges in `/etc/subuid` `/etc/subgid` for the user that
runs `benchbuild` in this mode. In addition, you need a working fuse installation. This involves
an installation of `libfuse` with its headers.
The `benchbuild bootstrap` command may help you with the installation and setup.

## Configuration

`benchbuild` can be configured in various ways: (1) command-line arguments, (2) configuration file in .json format, (3) environment variables.
You can dump the current active configuration with the command:

```bash
benchbuild run -d
```

# Documentation

For detailed API information please refer to the full
[documentation](https://polyjit.github.io/benchbuild):

You can dump this information in YAML format using the command:
```bash
benchbuild run -s
```

It dumps \_all\_ configuration to YAML, even those that are usually derived automatically (like UUIDs).
In the future, this will be avoided automatically.
For now, you should remove all ID related variables from the resulting YAML file.
The configuration file is searched from the current directory upwards automatically.
Some key configuration variables:

```
  BB_BUILD_DIR     The directory we place our temporary artifacts in.
  BB_TMP_DIR       The directory we place our downloads in.
  BB_CLEAN         Should the build directory be cleaned after the run?
  BB_CONFIG_FILE   Where is the config file? If you prefere an absolute location over automatic discovery.
  BB_DB_HOST       Hostname of the database
  BB_DB_NAME       Name of the database
  BB_DB_USER       Username of the database
  BB_DB_PASS       Password of the database
  BB_DB_ROLLBACK   For testing Rollback all db actions after a run.
  BB_JOBS          Number of threads to use for compiling / run-time testing.
```

You can set these in the .json config file or directly via environment
variables. However, make sure that the values you pass in from the
environment are valid JSON, or the configuration structure may ignore
your input (or break).

### SLURM Configuration

If you want to run experiments in parallel on a cluster managed by
SLURM, you can use BenchBuild to generate a bash script that is
compatible with SLURM's sbatch command. The following settings control
SLURM's configuration:

```
  BB_SLURM_ACCOUNT         The resource account log in to.
  BB_SLURM_CPUS_PER_TASK   How many cores/threads should we request per node?
  BB_SLURM_EXCLUSIVE       Should we request the node exclusively or share it with other tasks?
  BB_SLURM_MAX_RUNNING     We generate array-Jobs. This parameter controls the number of array elements that are allowed to run in parallel.
  BB_SLURM_MULTITHREAD     Should Hyper-Threading be enabled or not?
  BB_SLURM_NICE            Adjust our priority on the cluster manually.
  BB_SLURM_NICE_CLEAN      Adjust the priority of the clean jobs.
  BB_SLURM_NODE_DIR        Where can we place our artifacts on the node?
  BB_SLURM_PARTITION       Which partition should we run in?
  BB_SLURM_SCRIPT          Base name of our resulting batch script.
  BB_SLURM_TIMELIMIT       Enforce a timelimit on our batch jobs.
```

### Gentoo Configuration

BenchBuild supports compile-time experiments on the complete portage
tree of Gentoo Linux. You need to configure a few settings to make it
work:

```
  BB_GENTOO_AUTOTEST_LOC           A txt file that lists all gentoo package atoms that should be considered.
  BB_GENTOO_AUTOTEST_FTP_PROXY     Proxy server for gentoo downloads.
  BB_GENTOO_AUTOTEST_HTTP_PROXY    Proxy server for gentoo downloads.
  BB_GENTOO_AUTOTEST_RSYNC_PROXY   Proxy server for gentoo downloads.
```

#### Convert an automatic Gentoo project to a static one

Gentoo projects are generated dynamically based on the `AutoPortage`
class found in `pprof.gentoo.portage_gen`. If you want to define
run-time tests for a dynamically generated project, you need to convert
it to a static one, i.e., define a subclass of `AutoPortage` and add it
to the configuration.

```python
from pprof.projects.gentoo.portage_gen import AutoPortage

class BZip(AutoPortage):
  NAME = "app-arch"
  DOMAIN = "bzip2"

  def run_tests(self):
    """Add your custom test routines here."""
```

Now we just need to add this to the plugin registry via `benchbuild`'s
configuration file @ `CFG["plugins"]["projects"]`.
