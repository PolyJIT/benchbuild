# PPROF - PolyJIT Profiling #

[![Codacy Badge](https://api.codacy.com/project/badge/grade/0220d2cf77f543e182d93eb55edf4199)](https://www.codacy.com/app/simbuerg/benchbuild-study)
[![Documentation Status](https://readthedocs.org/projects/benchbuild-study/badge/?version=develop)](http://benchbuild-study.readthedocs.org/en/latest/?badge=develop)
[![Build Status](https://travis-ci.org/simbuerg/benchbuild-study.svg?branch=develop)](https://travis-ci.org/simbuerg/benchbuild-study)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/2c39c4c4d9724224a9ed58fea3db1216/snapshot/origin:develop:HEAD/badge.svg)](https://www.quantifiedcode.com/app/project/2c39c4c4d9724224a9ed58fea3db1216)

This is a small python framework for measuring various case studies using
PolyJIT. By design it encodes ways to download/configure and run arbitrary
projects with your desired compiler / runtime wrappers.

All results are stored in a PostgreSQL backend for further analysis. It is
possible to intercept the compilation process as well as the run-time
process of any project supported by the study.

As an example, benchbuild-study includes a shiny app that is able to explore
some results from an existing database with the already existing experiments.
Feel free to extend the set of projects & experiments to match your needs.

## Requirements ##

You need a working PostgreSQL installation (There is no special reason for
PostgreSQL, but the backend is not configurable at the moment).

In addition to the PostgreSQL server, you need libpqxx/libpq available for
the psycopg2 package that benchbuild uses to connect.

### Python Headers ###

For `pip install --user .` to succeed, python headers are required.

On Ubuntu you can install `python-dev` to get the correct headers.

## How to install ##

After you have installed all necessary libraries, you can just clone this
repo and install via pip.

```bash
git clone https://github.com/simbuerg/benchbuild-study
cd benchbuild-study
pip install --user .
```

This will pull in all necessary python libraries into your local python
installation.
The installed program to control the study is called ``benchbuild``.

##  Usage ##

The study supports the following subcommands.

### Build mode ###

This mode provides a simple way to build a working LLVM/Clang/Polly/Polli
installation from scratch. Everything will be built _static_ for the X86
target architecture. You can specify which compiler you want to use and which
buildsystem should be used (ninja is the default).

#### libPAPI ####

Some experiments require libPAPI to run. The `benchbuild build` command only
accepts a single prefix, therefore you might need to adjust some symlinks.

On Ubuntu you can install `libpapi` and create a symlink for libpapi.so
in `/usr/lib`

#### Boost ####

`benchbuild build` requires some headers from libboost. On Ubuntu you can
install `libboost-dev`.

#### libpqxx ####

`benchbuild build` requires `libpqxx` for polyjit to communicate with the
postgres database.

On Ubuntu you can install `libpqxx-dev`.

#### cmake ####

LLVM requires `cmake` to build.

#### ninja ####

The build mode uses the `ninja` build system by default, you can switch
to `make`, if needed.

```
$> benchbuild build --help
Build all dependences required to run the benchbuild study.
Usage:
    benchbuild build [SWITCHES]

Meta-switches:
    -h, --help                       Prints this help message and quits
    --help-all                       Print help messages of all subcommands and quit
    -v, --version                    Prints the program's version and quits

Switches:
    -B, --builddir DIRNAME:str       Where should we build our dependencies?; required
    -I, --isldir DIRNAME:str         Where is isl?
    -L, --likwiddir DIRNAME:str      Where is likwid?; required
    -P, --papidir DIRNAME:str        Where is libPAPI?; required
    -j, --jobs NUM:int               Number of jobs to use for building
    --use-gcc                        Use gcc to build llvm/clang
    --use-make                       Use make instead of ninja as build system
```

### Config mode ###

```
$> benchbuild config --help
Generate a default configuration that can be edited in a text editor.
Usage:
    benchbuild config [SWITCHES]

Meta-switches:
    -h, --help          Prints this help message and quits
    --help-all          Print help messages of all subcommands and quit
    -v, --version       Prints the program's version and quits

Switches:
    -o DIRNAME:str      Where to write the default config file? File type is
                        *.py

```

### Run mode ###

This is the default mode, after you have built a compatible llvm installation.
From there you need to decide which experiment(s) you want to run (-E switches)
and which project(s) you want to execute the experiments for (-P switches).
Optionally, you can specify a description for your experiment run. benchbuild annotate
the experiment in the database for later reuse.

```
Frontend for running experiments in the benchbuild study framework.
Usage:
    benchbuild run [SWITCHES]

Meta-switches:
    -h, --help                             Prints this help message and quits
    --help-all                             Print help messages of all subcommands and quit
    -v, --version                          Prints the program's version and quits

Switches:
    -B, --builddir DIRNAME:str             Where should we build
    -D, --description DESCRIPTION:str      A description for this experiment run
    -E, --experiment EXPERIMENTS:str       Specify experiments to run; may be given multiple times
    -G, --group GROUP:str                  Run a group of projects under the given experiments; requires --experiment
    -L, --llvmdir DIRNAME:str              Where is llvm?
    -P, --project PROJECTS:str             Specify projects to run; may be given multiple times; requires --experiment
    -S, --sourcedir DIRNAME:str            Where are the source files
    -T, --testdir DIRNAME:str              Where are the testinput files
    -k, --keep                             Keep intermediate results; requires --experiment
    -l, --list                             List available projects for experiment; requires --experiment
    --likwid-prefix DIRNAME:str            Where is likwid installed?
    --list-experiments                     List available experiments
    --llvm-srcdir DIRNAME:str              Where are the llvm source files
```

### Log view mode ###

This view mode can be used to inspect the stdout/stderr output of the projects
post-mortem, for experiments that support storage of project outputs (so far,
all of the experiments do).

```
$> benchbuild log --help
Frontend command to the benchbuild database.
Usage:
    benchbuild log [SWITCHES]

Meta-switches:
    -h, --help                                  Prints this help message and quits
    --help-all                                  Print help messages of all subcommands and quit
    -v, --version                               Prints the program's version and quits

Switches:
    -E, --experiment EXPERIMENTS:str            Experiments to fetch the log for.; may be given multiple times
    -P, --project PROJECTS:str                  Projects to fetch the log for.; may be given multiple times
    -e, --experiment-id EXPERIMENT_IDS:str      Experiment IDs to fetch the log for.; may be given multiple times
    -p, --project-id PROJECT_IDS:str            Project IDs to fetch the log for.; may be given multiple times
    -t, --type TYPES:{'stderr', 'stdout'}       Set the output types to print.; may be given multiple times
```

### Test mode ###

This mode can be used to generate regression tests for polyjit from the
database. Usually you won't need to use this.

```
Create regression tests for polyjit from the measurements database.
Usage:
    benchbuild test [SWITCHES]

Meta-switches:
    -h, --help                     Prints this help message and quits
    --help-all                     Print help messages of all subcommands and quit
    -v, --version                  Prints the program's version and quits

Switches:
    -L, --llvmdir DIRNAME:str      Where is llvm?
    -P, --prefix PREFIX:str        Prefix for our regression-test image.
```
