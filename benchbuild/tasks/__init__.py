"""
Benchbuild's tasks API

Base types:
    Task
    TaskGroup
    TaskManager
    TaskPolicy

Task groups:
    fail_group
    continue_group

Tasks:
    clean
    clean_extra
    compile_project
    echo
    make_builddir
    manage_experiment
    run_project

Context managers:
    ExperimentTransaction
    LogTasks
"""

from .actions import TaskPolicy, TaskGroup, Task, TaskManager
from .actions import fail_group, continue_group
from .actions import (echo, run_project, compile_project, make_builddir,
                      clean_extra, clean, manage_experiment)
from .actions import ExperimentTransaction, LogTasks
