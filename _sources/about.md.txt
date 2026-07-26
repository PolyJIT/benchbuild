# BenchBuild Documentation

BenchBuild is an open-source toolkit that helps with the management of case-studies used in software-driven empirical experiments.
BenchBuild was specifically designed to make defined experiments reusable between different
experiment setups. It mainly provides assistance with the following standard tasks found in empirical software experiments:

- Add a new case-study to an existing experiment setup.
- Add a new experiment to an existing body of case-studies.

## Design Philosophy

BenchBuild is designed with the following main properties in mind.

### A case-study doesn't know its experiment

If you add a new case-study, you should never have to rely on background information about the experiment you are about to run on it.
A new case-study is only concerned with its own setup of dependencies and execution during its run-time. A case-study controls where and what can be
intercepted by an experiment.

### An experiment doesn't know its case-studies

Adding a new experiment never should have any knowledge about the case-studies
it runs on.
A new experiment takes care of intercepting the compilation process and/or the
execution procedure of a given case-study. This only defines what is being done at the defined extension points at compile-time or run-time.

## Supported Python Versions

BenchBuild supports Python 3.7 and 3.8. Main development is focused on Python 3.8, but an effort is made to support 3.7 as long as major distributions like Debian Linux only ship with 3.7 by default.

## Getting started

See the [Installation guide]() for help getting BenchBuild up and running quickly.
