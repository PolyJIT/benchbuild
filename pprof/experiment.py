"""
An pprof.experiment defines a series of phases that constitute a pprof
compatible experiment. This is the default implementation of an experiment.

Clients can derive from class class::pprof.experiment.Experiment and override
the methods relvant to their experiment.

An experiment can have a variable number of phases / steps / substeps.

Phases / Steps / Substeps
-------------------------

All phases/steps/substeps support being used as a context manager. All 3 of
them catch ProcessExecutionErrors that may be thrown from plumbum, without
aborting the whole experiment. However, an error is tracked.

Actions
-------

An experiment performs the following actions in order:
    1. clean - Clean any previous runs that collide with our directory
    2. prepare - Prepare the experiment, this is a good place to copy relevant
                 files over for testing.
    3. run (run_tests) - Run the experiment. The 'meat' lies here. Override
        This to perform all your experiment needs.

"""
import warnings
import logging
import traceback as tb
from contextlib import contextmanager
from abc import abstractmethod
from os import path, listdir
import regex

from plumbum import local
from plumbum.cmd import mkdir, rmdir  # pylint: disable=E0401
from plumbum.commands.processes import ProcessExecutionError

from pprof.projects import *  # pylint: disable=W0401
from pprof.project import ProjectRegistry
from pprof.utils.run import GuardedRunException
from pprof.settings import CFG
from pprof.utils.db import persist_experiment


def newline(ostream):
    """
    Break the current line in the output stream.

    Don't reuse the current line, if :o: is not attached to a tty.

    Args:
        o (stream): The stream we insert a newline.

    Returns (stream): The stream
    """
    if ostream.isatty():
        ostream.write("\r\x1b[L")
    else:
        ostream.write("\n")
    return ostream


def static_var(varname, value):
    """
    Decorate something with a static variable.

    Example:
        .. code-block:: python

            @staticvar(bar, 0)
            def foo():
                foo.bar = 1
                return foo.bar

    Args:
        varname (str): The name of the static variable.
        value: The initial value of the static variable.

    Returns:
        A decorator that adds a new attribute to the given object.
    """

    def decorate(func):
        """ Decorate func. """
        setattr(func, varname, value)
        return func

    return decorate


@contextmanager
@static_var("name", "")
def phase(name, pname="FIXME: Unset", cleaner=None):
    """
    Introduce a new phase.

    This just introduces a new (cosmetic) phase distinction between
    different experiment phases.
    This can be used as a contextmanager to distinguish different experiment
    phases.

    Args:
        name (str): Name of the phase.
        pname (str): Project Name this phase will be started for.
        cleaner (callable): Cleaner callable that will be invoked as
            soon as the phase failed and we cannot recover.
    """
    phase.name = name

    from logging import error, info

    main_msg = "PHASE '{}' {}".format(name, pname)
    print(main_msg + " START")
    try:
        yield
        print(main_msg + " OK")
    except ProcessExecutionError as proc_ex:
        error(u"\n" + proc_ex.stderr)
        print(main_msg + " FAILED")
        cleaner()
        import sys
        sys.exit(-1)
    except (OSError, GuardedRunException) as os_ex:
        error(os_ex)
        print(main_msg + " FAILED")
        cleaner()
        import sys
        sys.exit(-1)


@contextmanager
@static_var("counter", 0)
@static_var("name", "")
def step(name):
    """
    Introduce a new step.

    This just introduces a new (cosmetic) step distinction between different
    experiment steps.
    This can be used as a contextmanager to distinguish different experiment
    steps.

    Args:
        name (str): The name of the step
    """
    from logging import info
    step.name = name

    main_msg = "    STEP '{}'".format(name)
    print(main_msg + " START")
    yield
    print(main_msg + " OK")


@contextmanager
@static_var("name", "")
def substep(name):
    """
    Introduce a new substep.

    This just introduces a new (cosmetic) substep distinction between different
    experiment steps.
    This can be used as a contextmanager to distinguish different experiment
    steps.

    Args:
        name (str): The name of the substep
    """
    substep.name = name
    from logging import info, error
    main_msg = "        SUBSTEP '{}'".format(name)

    print(main_msg + " START")
    try:
        yield
        print(main_msg + " OK")
    except ProcessExecutionError as proc_ex:
        error(proc_ex.stderr)
    except (OSError, GuardedRunException) as os_ex:
        error(os_ex)


def get_group_projects(group, experiment):
    """
    Get a list of project names for the given group.

    Filter the projects assigned to this experiment by group.

    Args:
        group (str): The group.
        experiment (pprof.Experiment): The experiment we draw our projects to
            filter from.

    Returns (list):
        A list of project names for the group that are supported by this
        experiment.
    """
    group = []
    projects = experiment.projects
    for name in projects:
        project = projects[name]

        if project.group_name == group:
            group.append(name)
    return group


class ExperimentRegistry(type):
    """Registry for pprof experiments."""

    experiments = {}

    def __init__(cls, name, bases, dict):
        """Registers a project in the registry."""
        super(ExperimentRegistry, cls).__init__(name, bases, dict)

        if cls.NAME is not None:
            ExperimentRegistry.experiments[cls.NAME] = cls


class Experiment(object, metaclass=ExperimentRegistry):
    """
    A series of commands executed on a project that form an experiment.

    The default implementation should provide a sane environment for all
    derivates.

    One important task executed by the basic implementation is setting up
    the default set of projects that belong to this project.
    As every project gets registered in the ProjectFactory, the experiment
    gets a list of experiment names that work as a filter.

    """
    NAME = None

    def __new__(cls, *args, **kwargs):
        """Create a new experiment instance and set some defaults."""
        new_self = super(Experiment, cls).__new__(cls)
        if cls.NAME is None:
            raise AttributeError(
                "{} @ {} does not define a NAME class attribute.".format(
                    cls.__name__, cls.__module__))
        new_self.name = cls.NAME
        return new_self

    def setup_commands(self):
        """
        Precompute some often used path variables used throughout all projects.
        """
        bin_path = path.join(str(CFG["llvm"]["dir"]), "bin")

        CFG["path"] = bin_path + ":" + str(CFG["path"])
        CFG["ld_library_path"] = ":".join([
            path.join(
                str(CFG["llvm"]["dir"]), "lib"), str(CFG["ld_library_path"])
        ])

    def __init__(self, projects=None, group=None):
        self.projects = {}
        self.setup_commands()
        self.sourcedir = CFG["src_dir"].value()
        self.builddir = path.join(str(CFG["build_dir"].value()), self.name)
        self.testdir = CFG["test_dir"].value()

        self.populate_projects(projects, group)

    def populate_projects(self, projects_to_filter=None, group=None):
        """
        Populate the list of projects that belong to this experiment.

        Args:
            projects_to_filter (list):
                List of projects we want to assign to this experiment.
                We intersect the list of projects with the list of supported
                projects to get the list of projects that belong to this
                experiment.
            group (str):
                In addition to the project filter, we provide a way to filter
                whole groups.
        """
        self.projects = {}

        projects = ProjectRegistry.projects
        if projects_to_filter:
            allkeys = set(list(projects.keys()))
            usrkeys = set(projects_to_filter)
            projects = {x: projects[x] for x in allkeys & usrkeys}

        if group:
            projects = {
                name: cls
                for name, cls in projects.items() if cls.GROUP == group
            }

        if projects_to_filter is None:
            projects_to_filter = []
        projects = {x: projects[x]
                    for x in projects
                    if projects[x].DOMAIN != "debug" or x in projects_to_filter
                    }

        self.projects = {k: projects[k](self) for k in projects}

    def clean_project(self, project):
        """
        Invoke the clean phase of the given project.

        Args:
            project (pprof.Project): The project we want to clean.
        """
        with local.env(PPROF_ENABLE=0):
            project.clean()

    def prepare_project(self, project):
        """
        Invoke the prepare phase of the given project.

        Args:
            project (pprof.Project): The project we want to prepare.
        """
        with local.env(PPROF_ENABLE=0):
            project.prepare()

    @abstractmethod
    def run_project(self, project):
        """
        Invoke the run phase of the given project.

        Args:
            project (pprof.Project): the project we want to run.
        """
        pass

    def run_this_project(self, project):
        """
        Execute the project wrapped in a database session.

        Args:
            project (pprof.Project): The project we wrap.
        """
        self.run_project(project)

    def map_projects(self, fun, pname=None):
        """
        Map a function over all projects.

        Args:
            fun: The function that is applied to all projects.
            pname (str): The project phase name.
        """
        from functools import partial
        for project_name in self.projects:
            prj = self.projects[project_name]

            def maybe_clean_on_error(project):
                if "clean" in CFG and CFG["clean"].value():
                    project.clean()

            with phase(pname, project_name, partial(maybe_clean_on_error,
                                                    prj)):
                llvm_libs = path.join(str(CFG["llvm"]["dir"]), "lib")
                ld_lib_path = str(CFG["ld_library_path"]) + ":" + llvm_libs
                with local.env(LD_LIBRARY_PATH=ld_lib_path,
                               PPROF_EXPERIMENT=self.name,
                               PPROF_PROJECT=prj.name):
                    fun(prj)

    def clean(self):
        """Clean the experiment."""
        self.map_projects(self.clean_project, "clean")
        if path.exists(self.builddir) and listdir(self.builddir) == []:
            try:
                rmdir(self.builddir)
            except ProcessExecutionError as ex:
                warnings.warn(str(ex), category=RuntimeWarning)
        else:
            logger = logging.getLogger(__name__)
            logger.info("Experiment directory '{}' is not clean.".format(
                self.builddir))



    def prepare(self):
        """
        Prepare the experiment.

        This includes creation of a build directory and setting up the logging.
        Afterwards we call the prepare method of the project.
        """
        if not path.exists(self.builddir):
            mkdir(self.builddir, retcode=None)

        self.map_projects(self.prepare_project, "prepare")

    def run(self):
        """
        Run the experiment on all registered projects.

        Setup the environment and call run_project method on all projects.
        """
        from datetime import datetime
        from logging import error, info

        experiment, session = persist_experiment(self)
        if experiment.begin is None:
            experiment.begin = datetime.now()
        else:
            experiment.begin = min(experiment.begin, datetime.now())
        session.add(experiment)
        session.commit()

        try:
            with local.env(PPROF_EXPERIMENT_ID=str(CFG["experiment"])):
                self.map_projects(self.run_this_project, "run")
        except KeyboardInterrupt:
            error("User requested termination.")
        except Exception:
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            formatted = "".join(tb.format_exception(exc_type, exc_value,
                                                    exc_traceback))
            warnings.warn(formatted, category=RuntimeWarning)
            print("Shutting down...")
        finally:
            if experiment.end is None:
                experiment.end = datetime.now()
            else:
                experiment.end = max(experiment.end, datetime.now())
            session.add(experiment)
            session.commit()


class RuntimeExperiment(Experiment):
    """ Additional runtime only features for experiments. """

    def get_papi_calibration(self, project, calibrate_call):
        """
        Get calibration values for PAPI based measurements.

        Args:
            project (Project):
                Unused (deprecated).
            calibrate_call (plumbum.cmd):
                The calibration command we will use.
        """
        with local.cwd(self.builddir):
            with local.env(PPROF_USE_DATABASE=0,
                           PPROF_USE_CSV=0,
                           PPROF_USE_FILE=0):
                calib_out = calibrate_call()

        calib_pattern = regex.compile(
            r'Real time per call \(ns\): (?P<val>[0-9]+.[0-9]+)')
        for line in calib_out.split('\n'):
            res = calib_pattern.search(line)
            if res:
                return res.group('val')
        return None

    def persist_calibration(self, project, cmd, calibration):
        """
        Persist the result of a calibration call.

        Args:
            project (pprof.Project):
                The calibration values will be assigned to this project.
            cmd (plumbum.cmd):
                The command we used to generate the calibration values.
            calibration (int):
                The calibration time in nanoseconds.
        """
        if calibration:
            from pprof.utils.db import create_run
            from pprof.utils import schema as s

            run, session = create_run(
                str(cmd), project.name, self.name, project.run_uuid)
            metric = s.Metric(name="papi.calibration.time_ns",
                              value=calibration,
                              run_id=run.id)
            session.add(metric)
            session.commit()
