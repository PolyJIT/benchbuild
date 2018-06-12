"""
The 'polyjit' experiment.

This experiment uses likwid to measure the performance of all binaries
when running with polyjit support enabled.
"""
import copy
import glob
import logging
import os
import uuid
from abc import abstractmethod

import sqlalchemy as sa
from plumbum import local

import benchbuild.extensions as ext
import benchbuild.utils.schema as schema
from benchbuild.experiment import Experiment
from benchbuild.utils.actions import Any, RequireAll
from benchbuild.utils.dict import ExtensibleDict, extend_as_list

LOG = logging.getLogger(__name__)

__REGIONS__ = sa.Table('regions', schema.metadata(),
                       sa.Column(
                           'run_id',
                           sa.Integer,
                           sa.ForeignKey(
                               "run.id",
                               onupdate="CASCADE",
                               ondelete="CASCADE"),
                           index=True,
                           primary_key=True), sa.Column(
                               'duration', sa.Numeric),
                       sa.Column('id', sa.Numeric, primary_key=True),
                       sa.Column('name', sa.String),
                       sa.Column('events', sa.BigInteger))


def verbosity_to_polyjit_log_level(verbosity: int):
    """Transfers the verbosity level to a useable polyjit format."""
    polyjit_log_levels = {
        0: "off",
        1: "error",
        2: "warn",
        3: "info",
        4: "debug",
        5: "trace",
        6: "trace",
    }
    return polyjit_log_levels[verbosity]


class PolyJITConfig(object):
    """Object that stores the configuraion of the JIT."""
    __config = ExtensibleDict(extend_as_list)

    @property
    def argv(self):
        """Getter for the configuration held by the config object."""
        return PolyJITConfig.__config

    def clear(self):
        PolyJITConfig.__config.clear()

    def value_to_str(self, key):
        """Prints the value of a given key."""
        if key not in self.argv:
            return ""
        value = self.argv[key]
        if isinstance(value, list):
            value = " ".join(value)
        LOG.debug(" %s=%s", key, value)
        return value


class ClearPolyJITConfig(PolyJITConfig, ext.Extension):
    def __call__(self, *args, **kwargs):
        self.clear()
        return self.call_next(*args, **kwargs)


class EnableJITDatabase(PolyJITConfig, ext.Extension):
    """The run and given extensions store polli's statistics to the database."""

    def __init__(self, *args, project=None, **kwargs):
        """Initialize the db object for the JIT."""
        super(EnableJITDatabase, self).__init__(
            *args, project=project, **kwargs)
        self.project = project

    def __call__(self, binary_command, *args, **kwargs):
        from benchbuild.settings import CFG
        experiment = self.project.experiment

        def deconstruct(connect_str):
            """Deconstruct a full PostgreSQL connect_str."""
            from parse import parse
            res = parse("{dialect}://{user}:{password}@{host}:{port}/{name}",
                        connect_str)
            return (res['dialect'], res['user'], res['password'], res['host'],
                    res['port'], res['name'])

        _, user, password, host, port, name = \
            deconstruct(CFG["db"]["connect_string"].value())
        pjit_args = [
            "-polli-db-experiment='{:s}'".format(experiment.name),
            "-polli-db-experiment-uuid='{:s}'".format(str(experiment.id)),
            "-polli-db-argv='{:s}'".format(str(binary_command)),
            "-polli-db-host='{:s}'".format(host),
            "-polli-db-port={:s}".format(port),
            "-polli-db-username={:s}".format(user),
            "-polli-db-password={:s}".format(password),
            "-polli-db-name='{:s}'".format(name),
        ]

        if self.project is not None:
            pjit_args.extend([
                "-polli-db-enable",
                "-polli-db-project='%s'" % self.project.name,
                "-polli-db-domain='%s'" % self.project.domain,
                "-polli-db-group='%s'" % self.project.group,
                "-polli-db-src-uri='%s'" % self.project.src_file,
                "-polli-db-run-group='%s'" % self.project.run_uuid
            ])
        else:
            LOG.error("Project was not set."
                      " Database activation will be invalid.")

        with self.argv(PJIT_ARGS=pjit_args):
            return self.call_next(binary_command, *args, **kwargs)


class EnablePolyJIT_Opt(PolyJITConfig, ext.Extension):
    """Call the child extensions with an activated PolyJIT."""

    def __call__(self, *args, **kwargs):
        ret = None
        with self.argv(PJIT_ARGS=["-polli-use-polly-options=false"]):
            with local.env(PJIT_ARGS=self.value_to_str('PJIT_ARGS')):
                ret = self.call_next(*args, **kwargs)
        return ret


class EnablePolyJIT(PolyJITConfig, ext.Extension):
    """Call the child extensions with an activated PolyJIT."""

    def __call__(self, *args, **kwargs):
        ret = None
        with local.env(PJIT_ARGS=self.value_to_str('PJIT_ARGS')):
            ret = self.call_next(*args, **kwargs)
        return ret


class DisableDelinearization(PolyJITConfig, ext.Extension):
    """Deactivate the JIT for the following extensions."""

    def __call__(self, *args, **kwargs):
        ret = None
        with self.argv(PJIT_ARGS=["-polli-no-delinearization"]):
            with local.env(PJIT_ARGS=self.value_to_str('PJIT_ARGS')):
                ret = self.call_next(*args, **kwargs)
        return ret


class DisablePolyJIT(PolyJITConfig, ext.Extension):
    """Deactivate the JIT for the following extensions."""

    def __call__(self, *args, **kwargs):
        ret = None
        with self.argv(PJIT_ARGS=["-polli-no-specialization"]):
            with local.env(PJIT_ARGS=self.value_to_str('PJIT_ARGS')):
                ret = self.call_next(*args, **kwargs)
        return ret


class RegisterPolyJITLogs(PolyJITConfig, ext.LogTrackingMixin, ext.Extension):
    """Extends the following RunWithTime extensions with extra PolyJIT logs."""

    def __call__(self, *args, **kwargs):
        """Redirect to RunWithTime, but register additional logs."""
        from benchbuild.settings import CFG

        log_level = verbosity_to_polyjit_log_level(CFG["verbosity"].value())

        curdir = os.path.realpath(os.path.curdir)
        files_before = glob.glob(os.path.join(curdir, "polyjit.*.log"))

        with self.argv(PJIT_ARGS=[
                "-polli-enable-log", "-polli-log-level={}".format(log_level)
        ]):
            ret = self.call_next(*args, **kwargs)
        files = glob.glob(os.path.join(curdir, "polyjit.*.log"))
        files = [
            new_file for new_file in files if new_file not in files_before
        ]

        for file in files:
            self.add_log(file)

        return ret


class PolyJIT(Experiment):
    """The polyjit experiment."""

    @classmethod
    def init_project(cls, project):
        """
        Execute the benchbuild experiment.

        We perform this experiment in 2 steps:
            1. with likwid disabled.
            2. with likwid enabled.

        Args:
            project: The project we initialize.

        Returns:
            The initialized project.
        """
        project.ldflags += ["-lpjit", "-lgomp"]
        project.cflags = [
            "-fno-omit-frame-pointer", "-rdynamic", "-Xclang", "-load",
            "-Xclang", "LLVMPolly.so", "-Xclang", "-load", "-Xclang",
            "LLVMPolyJIT.so", "-O3", "-mllvm", "-polli-enable-log", "-mllvm",
            "-polli"
        ]
        return project

    @abstractmethod
    def actions_for_project(self, project):
        pass


class PolyJITSimple(PolyJIT):
    """Simple runtime-testing with PolyJIT."""
    NAME = "pj-simple"
    SCHEMA = [__REGIONS__]

    def actions_for_project(self, project):
        from benchbuild.settings import CFG

        project = PolyJIT.init_project(project)
        project.run_uuid = uuid.uuid4()
        log_level = verbosity_to_polyjit_log_level(CFG["verbosity"].value())

        project.cflags += [
            "-mllvm", "-polli-log-level={}".format(log_level), "-mllvm",
            "-stats"
        ]

        cfg = {
            "cflags": project.cflags,
            "recompilation": "enabled",
            "specialization": "enabled"
        }

        pjit_extension = \
            ext.RuntimeExtension(project, self, config=cfg) \
            << EnablePolyJIT() \
            << EnableJITDatabase(project=project) \
            << RegisterPolyJITLogs() \
            << ext.LogAdditionals() \
            << ClearPolyJITConfig() \
            << ext.RunWithTime()

        project.runtime_extension = ext.RunWithTime(pjit_extension)
        return PolyJITSimple.default_runtime_actions(project)


class PolyJITFull(PolyJIT):
    """
    An experiment that executes all projects with PolyJIT support.

    This is our default experiment for speedup measurements.
    """

    NAME = "pj"
    SCHEMA = [__REGIONS__]

    def actions_for_project(self, project):
        from benchbuild.settings import CFG

        project.cflags = ["-O3", "-fno-omit-frame-pointer"]

        actns = []
        rawp = copy.deepcopy(project)
        rawp.run_uuid = uuid.uuid4()
        rawp.runtime_extension = \
            ext.RuntimeExtension(
                rawp, self, config={"jobs": 1, "name": "Baseline O3"}) \
            << ext.SetThreadLimit(config={"jobs": 1}) \
            << ext.RunWithTime()
        actns.append(RequireAll(self.default_runtime_actions(rawp)))

        pollyp = copy.deepcopy(project)
        pollyp.run_uuid = uuid.uuid4()
        pollyp.cflags = [
            "-Xclang", "-load", "-Xclang", "LLVMPolly.so", "-mllvm", "-polly",
            "-mllvm", "-polly-parallel"
        ]
        pollyp.runtime_extension = \
            ext.RuntimeExtension(
                pollyp, self, config={"jobs": 1, "name": "Polly (Parallel)"}) \
            << ext.SetThreadLimit(config={"jobs": 1}) \
            << ext.RunWithTime()
        actns.append(RequireAll(self.default_runtime_actions(pollyp)))

        jitp = copy.deepcopy(project)
        jitp = PolyJIT.init_project(jitp)
        norecomp = copy.deepcopy(jitp)
        norecomp.cflags += ["-mllvm", "-polli-no-recompilation"]

        for i in range(2, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(norecomp)
            cp.run_uuid = uuid.uuid4()
            cfg = {
                "jobs": i,
                "cores": str(i - 1),
                "cores-config": str(i),
                "recompilation": "disabled",
                "name": "PolyJIT (No Recompilation)"
            }

            cp.runtime_extension = \
                ext.RuntimeExtension(cp, self, config=cfg) \
                << ext.SetThreadLimit(config=cfg) \
                << DisablePolyJIT() \
                << EnableJITDatabase(project=cp) \
                << ClearPolyJITConfig() \
                << ext.RunWithTime() \
                << RegisterPolyJITLogs() \
                << ext.LogAdditionals()
            actns.append(RequireAll(self.default_runtime_actions(cp)))

        for i in range(2, int(str(CFG["jobs"])) + 1):
            cp = copy.deepcopy(jitp)
            cp.run_uuid = uuid.uuid4()
            cfg = {
                "jobs": i,
                "cores": str(i - 1),
                "cores-config": str(i),
                "recompilation": "enabled",
                "name": "PolyJIT (Recompilation)"
            }

            cp.runtime_extension = \
                ext.RuntimeExtension(cp, self, config=cfg) \
                << ext.SetThreadLimit(config=cfg) \
                << EnablePolyJIT() \
                << EnableJITDatabase(project=cp) \
                << ClearPolyJITConfig() \
                << RegisterPolyJITLogs() \
                << ext.LogAdditionals()
            actns.append(RequireAll(self.default_runtime_actions(cp)))

        return [Any(actions=actns)]
