#!/usr/bin/env python
# encoding: utf-8

from plumbum import FG, local
from plumbum.commands import ProcessExecutionError
from plumbum.cmd import find, echo, rm, mkdir, rmdir, cp, ln, cat, make, chmod

from os import path, listdir
from glob import glob
from functools import wraps
from pplog import log_with
from settings import config

import sys
import logging

# Configure the log
formatter = logging.Formatter('%(asctime)s - %(levelname)s :: %(message)s')

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)

log = logging.getLogger(__name__)
log.addHandler(handler)

PROJECT_OPT_F_EXT = ".opt"
PROJECT_ASM_F_EXT = ".s"
PROJECT_OBJ_F_EXT = ".o"
PROJECT_TAR_F_EXT = ".tar.gz"
PROJECT_LIKWID_F_EXT = ".txt"
PROJECT_CSV_F_EXT = ".csv"
PROJECT_INST_F_EXT = ".inst"
PROJECT_BIN_F_EXT = ".bin"
PROJECT_PREOPT_F_EXT = ".preopt"
PROJECT_TIME_F_EXT = ".time"
PROJECT_PROFILE_F_EXT = ".profile.out"
PROJECT_CALLS_F_EXT = ".calls"
PROJECT_RESULT_F_EXT = ".result"
PROJECT_CALIB_CALLS_F_EXT = ".calibrate.calls"
PROJECT_CALIB_PROFILE_F_EXT = ".calibrate.profile.out"

class ProjectFactory:
    factories = {}
    def addFactory(id, projectFactory):
        ProjectFactory.factories[id] = projectFactory
    addFactory = staticmethod(addFactory)

    def createProject(id, exp):
        if not ProjectFactory.factories.has_key(id):
            ProjectFactory.factories[id] = \
                    eval(id + '.Factory()')
            return ProjectFactory.factories[id].create(self, exp)
    createProject = staticmethod(createProject)

class Project(object):

    """ A project defines how run-time testing and cleaning is done for this
        IR project
    """

    def __init__(self, exp, name, domain, group=None):
        self.experiment = exp
        self.name = name
        self.domain = domain
        self.group_name = group

        self.sourcedir = path.join(config["sourcedir"], self.name)
        self.builddir = path.join(config["builddir"], exp.name, self.name)
        if group:
            self.testdir = path.join(config["testdir"], domain, group, name)
        else:
            self.testdir = path.join(config["testdir"], domain, name)

        self.products = set()
        self.setup_derived_filenames()

    def setup_derived_filenames(self):
        self.base_f = path.join(self.sourcedir, self.name + ".bc")
        self.run_f = path.join(self.builddir, self.name)
        self.result_f = self.run_f + PROJECT_RESULT_F_EXT
        self.optimized_f = self.run_f + PROJECT_OPT_F_EXT
        self.asm_f = self.run_f + PROJECT_ASM_F_EXT
        self.obj_f = self.run_f + PROJECT_OBJ_F_EXT
        self.bin_f = self.run_f + PROJECT_BIN_F_EXT
        self.time_f = self.run_f + PROJECT_TIME_F_EXT
        self.calibrate_prof_f = self.run_f + PROJECT_CALIB_PROFILE_F_EXT
        self.calibrate_calls_f = self.run_f + PROJECT_CALIB_CALLS_F_EXT
        self.profbin_f = self.bin_f + PROJECT_PROFILE_F_EXT
        self.csv_f = self.run_f + PROJECT_CSV_F_EXT
        self._prof_f = self.run_f + PROJECT_PROFILE_F_EXT
        self._calls_f = self.run_f + PROJECT_CALLS_F_EXT
        self.likwid_f = self.run_f + PROJECT_LIKWID_F_EXT

        self.products.clear()
        self.products.add(self.run_f)
        self.products.add(self.optimized_f)
        self.products.add(self.bin_f)
        self.products.add(self.time_f)
        self.products.add(self.profbin_f)
        self.products.add(self.prof_f)
        self.products.add(self.likwid_f)
        self.products.add(self.csv_f)
        self.products.add(self.calls_f)
        self.products.add(self.result_f)
        self.products.add(self.asm_f)
        self.products.add(self.obj_f)

    def get_file_content(self, ifile):
        lines = []
        if path.exists(ifile):
            with open(ifile) as f:
                lines = "".join(f.readlines()).strip().split()
        return lines

    @property
    def prof_f(self):
      return self._prof_f

    @prof_f.setter
    def prof_f(self, value):
      old = self.prof_f
      self._prof_f = value
      if old in self.products:
        self.products.remove(old)
      self.products.add(value)

    @property
    def calls_f(self):
      return self._calls_f

    @calls_f.setter
    def calls_f(self, value):
      old = self.prof_f
      self._calls_f = value
      self.products.remove(old)
      self.products.add(value)

    @property
    def ld_flags(self):
        ldflags = path.join(self.sourcedir, self.name + ".pprof")
        return self.get_file_content(ldflags)

    @property
    def polli_flags(self):
        polliflags = path.join(self.sourcedir, self.name + ".polli")
        return self.get_file_content(polliflags)

    @log_with(log)
    def run(self, experiment):
        with local.cwd(self.builddir):
            experiment & FG

    @log_with(log)
    def clean(self):
        dirs_to_remove = set([])

        for product in self.products:
            if path.exists(product) and not path.isdir(product):
                rm[product] & FG
            elif path.isdir(product):
                dirs_to_remove.add(product)

        for d in dirs_to_remove:
            if listdir(d) == []:
                rmdir[d] & FG

        if path.exists(self.builddir) and listdir(self.builddir) == []:
            rmdir[self.builddir] & FG
        elif path.exists(self.builddir) and listdir(self.builddir) != []:
            log.warn(self.name + " project unclean, force removing " +
                     self.builddir)
            rm["-rf", self.builddir] & FG

    @log_with(log)
    def prepare(self):
        if not path.exists(self.builddir):
            mkdir[self.builddir] & FG


class PprofGroup(Project):
    path_suffix = "src"

    def __init__(self, exp, name, domain):
        super(PprofGroup, self).__init__(exp, name, domain)
        self.sourcedir = path.join(config["sourcedir"], "src", name)
        self.setup_derived_filenames()


class Bzip2(PprofGroup):

    """ Bzip2 """

    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]

    class Factory:
        def create(self, exp):
            obj = Bzip2(exp, "bzip2", "compression")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")

            return obj
    ProjectFactory.addFactory("Bzip2", Factory())

    @log_with(log)
    def clean(self):
        for x in self.testfiles:
            self.products.add(path.join(self.builddir, x))
            self.products.add(path.join(self.builddir, x + ".bz2"))

        super(Bzip2, self).clean()

    @log_with(log)
    def prepare(self):
        super(Bzip2, self).prepare()
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp[testfiles, self.builddir] & FG

    @log_with(log)
    def run(self, experiment):
        with local.cwd(self.builddir):
            # Compress
            experiment["-f", "-z", "-k", "--best", "text.html"] & FG
            experiment["-f", "-z", "-k", "--best", "chicken.jpg"] & FG
            experiment["-f", "-z", "-k", "--best", "control"] & FG
            experiment["-f", "-z", "-k", "--best", "input.source"] & FG
            experiment["-f", "-z", "-k", "--best", "liberty.jpg"] & FG

            # Decompress
            experiment["-f", "-k", "--decompress", "text.html.bz2"] & FG
            experiment["-f", "-k", "--decompress", "chicken.jpg.bz2"] & FG
            experiment["-f", "-k", "--decompress", "control.bz2"] & FG
            experiment["-f", "-k", "--decompress", "input.source.bz2"] & FG
            experiment["-f", "-k", "--decompress", "liberty.jpg.bz2"] & FG


class Gzip(PprofGroup):

    """ Gzip """

    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]

    class Factory:
        def create(self, exp):
            obj = Gzip(exp, "gzip", "compression")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Gzip", Factory())

    def clean(self):
        for x in self.testfiles:
            self.products.add(path.join(self.builddir, x))
            self.products.add(path.join(self.builddir, x + ".gz"))

        super(Gzip, self).clean()

    def prepare(self):
        super(Gzip, self).prepare()
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp[testfiles, self.builddir] & FG

    def run(self, experiment):
        with local.cwd(self.builddir):
            # Compress
            experiment["-f", "-k", "--best", "text.html"] & FG
            experiment["-f", "-k", "--best", "chicken.jpg"] & FG
            experiment["-f", "-k", "--best", "control"] & FG
            experiment["-f", "-k", "--best", "input.source"] & FG
            experiment["-f", "-k", "--best", "liberty.jpg"] & FG

            # Decompress
            experiment["-f", "-k", "--decompress", "text.html.gz"] & FG
            experiment["-f", "-k", "--decompress", "chicken.jpg.gz"] & FG
            experiment["-f", "-k", "--decompress", "control.gz"] & FG
            experiment["-f", "-k", "--decompress", "input.source.gz"] & FG
            experiment["-f", "-k", "--decompress", "liberty.jpg.gz"] & FG


class SevenZip(PprofGroup):

    """ 7Zip """

    class Factory:
        def create(self, exp):
            obj = SevenZip(exp, "7z", "compression")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("SevenZip", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            experiment["b", "-mmt1"] & FG

class SpiderMonkey(PprofGroup):
    class Factory:
        def create(self, exp):
            obj = SpiderMonkey(exp, "js", "compilation")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("SpiderMonkey", Factory())

    def prepare(self):
        super(SpiderMonkey, self).prepare()
        config_path = path.join(self.testdir, "config")
        cp["-var", config_path, self.builddir] & FG
        self.products.add(path.join(config_path, "autoconf.mk"))
        self.products.add(config_path)

    def run(self, experiment):
        with local.cwd(self.builddir):
            for jsfile in glob(path.join(self.testdir, "sunspider", "*.js")):
                (experiment < jsfile) & FG

            sh_script = path.join(self.builddir, self.bin_f + ".sh")
            (echo["#!/bin/sh"] > sh_script) & FG
            (echo[str(experiment) + " $*"] >> sh_script) & FG
            chmod("+x", sh_script)
            jstests = local[path.join(self.testdir, "tests", "jstests.py")]
            jstests[sh_script] & FG(retcode=None)

    ProjectFactory.addFactory("SpiderMonkey", Factory())

class Ruby(PprofGroup):
    class Factory:
        def create(self, exp):
            obj = Ruby(exp, "ruby", "compilation")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Ruby", Factory())

    def run(self, experiment):
        from plumbum.cmd import ruby

        with local.cwd(self.builddir):
            with local.env(RUBYOPT=""):
                sh_script = path.join(self.builddir, self.bin_f + ".sh")
                (echo["#!/bin/sh"] > sh_script) & FG
                (echo[str(experiment) + " $*"] >> sh_script) & FG
                chmod("+x", sh_script)

                ruby[path.join(self.testdir, "benchmark", "run.rb"),
                     "--ruby=\""+str(sh_script)+"\"",
                     "--opts=\"-I"+path.join(self.testdir, "lib") +
                     " -I"+path.join(self.testdir, ".")+
                     " -I"+path.join(self.testdir, ".ext", "common")+
                     "\"", "-r"] & FG

class SDCC(PprofGroup):
    class Factory:
        def create(self, exp):
            return SDCC(exp, "sdcc", "compilation")
    ProjectFactory.addFactory("SDCC", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            log.debug("FIXME: invalid LLVM IR, regenerate from source")
            log.debug("FIXME: test incomplete, port from sdcc/Makefile")
            experiment & FG

class TCC(PprofGroup):
    class Factory:
        def create(self, exp):
            return TCC(exp, "tcc", "compilation")
    ProjectFactory.addFactory("TCC", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            log.debug("FIXME: test incomplete, port from tcc/Makefile")
            experiment & FG

class XZ(PprofGroup):

    """ XZ """

    testfiles = ["text.html", "chicken.jpg", "control", "input.source",
                 "liberty.jpg"]

    class Factory:
        def create(self, exp):
            obj = XZ(exp, "xz", "compression")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("XZ", Factory())

    def clean(self):
        for x in self.testfiles:
            self.products.add(path.join(self.builddir, x))
            self.products.add(path.join(self.builddir, x + ".xz"))

        super(XZ, self).clean()

    def prepare(self):
        super(XZ, self).prepare()
        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        cp[testfiles, self.builddir] & FG

    def run(self, experiment):
        with local.cwd(self.builddir):
            # Compress
            experiment["-f", "-k", "--compress", "-e", "-9", "text.html"] & FG
            experiment["-f", "-k", "--compress", "-e", "-9", "chicken.jpg"] & FG
            experiment["-f", "-k", "--compress", "-e", "-9", "control"] & FG
            experiment[
                "-f",
                "-k",
                "--compress",
                "-e",
                "-9",
                "input.source"] & FG
            experiment["-f", "-k", "--compress", "-e", "-9", "liberty.jpg"] & FG

            # Decompress
            experiment["-f", "-k", "--decompress", "text.html.xz"] & FG
            experiment["-f", "-k", "--decompress", "chicken.jpg.xz"] & FG
            experiment["-f", "-k", "--decompress", "control.xz"] & FG
            experiment["-f", "-k", "--decompress", "input.source.xz"] & FG
            experiment["-f", "-k", "--decompress", "liberty.jpg.xz"] & FG


class SQLite3(PprofGroup):

    """ SQLite3 """

    class Factory:
        def create(self, exp):
            obj = SQLite3(exp, "sqlite3", "database")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("SQLite3", Factory())

class X264(PprofGroup):

    """ x264 """

    inputfiles = ["tbbt-small.y4m"]

    class Factory:
        def create(self, exp):
            obj = X264(exp, "x264", "multimedia")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("X264", Factory())

    def prepare(self):
        super(X264, self).prepare()

        testfiles = [path.join(self.testdir, x) for x in self.inputfiles]
        for testfile in testfiles:
            cp[testfile, self.builddir] & FG

    def clean(self):
        for x in self.inputfiles:
            self.products.add(path.join(self.builddir, x))

        super(X264, self).clean()

    def run(self, experiment):
        testfiles = [path.join(self.testdir, x) for x in self.inputfiles]
        # TODO: Prepare test videos
        for ifile in testfiles:
            with local.cwd(self.builddir):
                experiment[
                    ifile,
                    "--threads", "1",
                    "-o", "/dev/null",
                    "--frames", "5",
                    "--crf", "30",
                    "-b1", "-m1", "-r1", "--me", "dia", "--no-cabac",
                    "--direct", "temporal", "--ssim", "--no-weightb"] & FG
                experiment[
                    ifile,
                    "--threads", "1",
                    "-o", "/dev/null",
                    "--frames", "5",
                    "--crf", "16",
                    "-b2", "-m3", "-r3", "--me", "hex", "--no-8x8dct",
                    "--direct", "spatial", "--no-dct-decimate", "-t0",
                    "--slice-max-mbs", "50"] & FG
                experiment[
                    ifile,
                    "--threads", "1",
                    "-o", "/dev/null",
                    "--frames", "5",
                    "--crf", "26",
                    "-b4", "-m5", "-r2", "--me", "hex", "--cqm", "jvt",
                    "--nr", "100", "--psnr", "--no-mixed-refs",
                    "--b-adapt", "2", "--slice-max-size", "1500"] & FG
                experiment[
                    ifile,
                    "--threads", "1", "-o", "/dev/null", "--frames", "5",
                    "--crf", "18", "-b3", "-m9", "-r5", "--me", "umh",
                    "-t1", "-A", "all", "--b-pyramid", "normal",
                    "--direct", "auto", "--no-fast-pskip", "--no-mbtree"] & FG
                experiment[
                    ifile,
                    "--threads", "1", "-o", "/dev/null", "--frames", "5",
                    "--crf", "22", "-b3", "-m7", "-r4", "--me", "esa", "-t2",
                    "-A", "all", "--psy-rd", "1.0:1.0", "--slices", "4"] & FG
                experiment[
                    ifile,
                    "--threads", "1", "-o", "/dev/null", "--frames", "5",
                    "--crf", "24", "-b3", "-m10", "-r3", "--me", "tesa",
                    "-t2"] & FG
                experiment[
                    ifile,
                    "--threads", "1", "-o", "/dev/null", "--frames", "5",
                    "-q0", "-m9", "-r2", "--me", "hex", "-Aall"] & FG
                experiment[
                    ifile,
                    "--threads", "1", "-o", "/dev/null", "--frames", "5",
                    "-q0", "-m2", "-r1", "--me", "hex", "--no-cabac"] & FG

class Lulesh(PprofGroup):

    """ Lulesh """

    class Factory:
        def create(self, exp):
            obj = Lulesh(exp, "lulesh", "scientific")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Lulesh", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            experiment["20"] & FG


class LuleshOMP(PprofGroup):

    """ Lulesh-OMP """

    class Factory:
        def create(self, exp):
            return LuleshOMP(exp, "lulesh-omp", "scientific")
    ProjectFactory.addFactory("LuleshOMP", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            experiment["20"] & FG


class Linpack(PprofGroup):

    """ Linpack (C-Version) """

    class Factory:
        def create(self, exp):
            obj = Linpack(exp, "linpack", "scientific")

            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")

            return obj
    ProjectFactory.addFactory("Linpack", Factory())

class LevelDB(PprofGroup):
    class Factory:
        def create(self, exp):
            obj = LevelDB(exp, "leveldb", "database")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("LevelDB", Factory())

class Ccrypt(PprofGroup):

    """ ccrypt benchmark """

    check_f = "check"

    class Factory:
        def create(self, exp):
            obj = Ccrypt(exp, "ccrypt", "encryption")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Ccrypt", Factory())

    def prepare(self):
        super(Ccrypt, self).prepare()
        check_f = path.join(self.testdir, self.check_f)
        ln("-s", check_f, path.join(self.builddir, self.check_f))

    def clean(self):
        check_f = path.join(self.builddir, self.check_f)
        self.products.add(check_f)

        super(Ccrypt, self).clean()

    def run(self, experiment):
        with local.cwd(self.builddir):
            command = " ".join(experiment["-f"].formulate())
            crypt_check = path.join(self.builddir, "check", "ccrypt-check.sh")
            length_check = path.join(self.builddir, "check", "length-check.sh")
            with local.env(CCRYPT=command,
                           srcdir=path.join(self.builddir, "check")):
                local[crypt_check] & FG
                local[length_check] & FG


class Crafty(PprofGroup):

    """ crafty benchmark """

    class Factory:
        def create(self, exp):
            obj = Crafty(exp, "crafty", "scientific")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Crafty", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            (cat[path.join(self.testdir, "test1.sh")] | experiment) & FG
            (cat[path.join(self.testdir, "test2.sh")] | experiment) & FG


class Crocopat(PprofGroup):

    """ crocopat benchmark """

    class Factory:
        def create(self, exp):
            obj = Crocopat(exp, "crocopat", "verification")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Crocopat", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            programs = glob(path.join(self.testdir, "programs", "*.rml"))
            projects = glob(path.join(self.testdir, "projects", "*.rsf"))
            for program in programs:
                for project in projects:
                    (cat[project] | experiment[program]) & FG(retcode=None)


class Lammps(PprofGroup):

    """ LAMMPS benchmark """

    class Factory:
        def create(self, exp):
            return Lammps(exp, "lammps", "scientific")
    ProjectFactory.addFactory("Lammps", Factory())

    def run(self, experiment):
        with local.cwd(self.builddir):
            tests = glob(path.join(self.testdir, "in.*"))
            for test in tests:
                (experiment < test) & FG


class LibAV(PprofGroup):

    """ LibAV benchmark """

    class Factory:
        def create(self, exp):
            return LibAV(exp, "avconv", "multimedia")
    ProjectFactory.addFactory("LibAV", Factory())

    @log_with(log)
    def clean(self):
        testfiles = path.join(self.testdir)
        btestfiles = glob(path.join(self.builddir, "*"))

        self.products.add(path.join(self.builddir, "tests"))
        for f in btestfiles:
            if not path.isdir(f):
                self.products.add(f)

        self.products.add(path.join(self.builddir, "Makefile.libav"))
        super(LibAV, self).clean()

    @log_with(log)
    def prepare(self):
        super(LibAV, self).prepare()

        testfiles = glob(path.join(self.testdir, "*"))

        for f in testfiles:
            cp["-a", f, self.builddir] & FG
        cp[path.join(self.sourcedir, "Makefile.libav"), self.builddir] & FG

    @log_with(log)
    def run(self, experiment):
        with local.cwd(self.builddir):
            with local.env(TESTDIR=self.builddir):
                echo["#!/bin/sh"] >> path.join(self.builddir, self.name) & FG
                echo[str(experiment)] >> path.join(self.builddir, self.name) & FG
                chmod["+x", path.join(self.builddir, self.name)] & FG
                make["-i", "-f", "Makefile.libav", "fate"] & FG


class Minisat(PprofGroup):

    """ minisat benchmark """

    class Factory:
        def create(self, exp):
            obj = Minisat(exp, "minisat", "verification")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Minisat", Factory())

    def run(self, experiment):
        testfiles = glob(path.join(self.testdir, "*.cnf.gz"))
        for f in testfiles:
            with local.cwd(self.builddir):
                (experiment < f) & FG(retcode=[10,20])


class MCryptAES(PprofGroup):

    """ mcrypt-aes benchmark """

    class Factory:
        def create(self, exp):
            obj = MCryptAES(exp, "mcrypt-aes", "encryption")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("MCryptAES", Factory())


class MCryptCiphers(PprofGroup):

    """ mcrypt-ciphers benchmark """

    class Factory:
        def create(self, exp):
            obj = MCryptCiphers(exp, "mcrypt-ciphers", "encryption")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("MCryptCiphers", Factory())


class Postgres(PprofGroup):

    """ postgres benchmark """

    testfiles = ["pg_ctl", "dropdb", "createdb", "pgbench"]

    class Factory:
        def create(self, exp):
            return Postgres(exp, "postgres", "database")
    ProjectFactory.addFactory("Postgres", Factory())

    def clean(self):
        testfiles = [path.join(self.builddir, x) for x in self.testfiles]
        for f in testfiles:
            self.products.add(f)
        self.products.add(path.join(self.builddir, self.name + ".sh"))

        super(Postgres, self).clean()

    def prepare(self):
        super(Postgres, self).prepare()

        testfiles = [path.join(self.testdir, x) for x in self.testfiles]
        for f in testfiles:
            cp["-a", f, self.builddir] & FG

    def run(self, experiment):
        with local.cwd(self.builddir):
            echo("foo")
            pg_ctl = local[path.join(self.builddir, "pg_ctl")]
            dropdb = local[path.join(self.builddir, "dropdb")]
            createdb = local[path.join(self.builddir, "createdb")]
            pgbench = local[path.join(self.builddir, "pgbench")]

            bin_name = path.join(self.builddir, self.name + ".sh")
            test_data = path.join(self.testdir, "test-data")

            echo["#!/bin/sh"] >> bin_name & FG
            echo[str(experiment)] >> bin_name & FG
            chmod("+x", bin_name)

            num_clients = 1
            num_transactions = 1000000

            pg_ctl("stop", "-t", 360, "-w", "-D", test_data, retcode=None)
            try:
                with local.cwd(test_data):
                    pg_ctl["start", "-p", bin_name, "-w", "-D", test_data] & FG
                dropdb["pgbench"] & FG(retcode=None)
                createdb["pgbench"] & FG
                pgbench["-i", "pgbench"] & FG
                pgbench[
                    "-c",
                    num_clients,
                    "-S",
                    "-t",
                    num_transactions,
                    "pgbench"] & FG
                dropdb["pgbench"] & FG
                pg_ctl["stop", "-t", 360, "-w", "-D", test_data] & FG
            except Exception:
                pg_ctl("stop", "-t", 360, "-w", "-D", test_data)
                raise


class Povray(PprofGroup):

    """ povray benchmark """

    class Factory:
        def create(self, exp):
            obj = Povray(exp, "povray", "multimedia")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Povray", Factory())

    def prepare(self):
        super(Povray, self).prepare()
        cp["-ar", path.join(self.testdir, "cfg"), self.builddir] & FG
        cp["-ar", path.join(self.testdir, "etc"), self.builddir] & FG
        cp["-ar", path.join(self.testdir, "scenes"), self.builddir] & FG
        cp["-ar", path.join(self.testdir, "share"), self.builddir] & FG
        cp["-ar", path.join(self.testdir, "test"), self.builddir] & FG

    def run(self, experiment):
        tmpdir = path.join(self.builddir, "tmp")
        povini = path.join(self.builddir, "cfg", ".povray", "3.6", "povray.ini")

        mkdir(tmpdir, retcode=None)
        with local.cwd(self.builddir):
            bin_name = path.join(self.builddir, self.name + ".sh")
            scene_dir = path.join(self.builddir, "share", "povray-3.6",
                                  "scenes")

            echo["#!/bin/sh"] >> bin_name & FG
            echo[str(experiment) + " $*"] >> bin_name & FG
            chmod("+x", bin_name)

            render = local[path.join(self.builddir, "test", "scripts",
                                     "render_scene.sh")]
            pov_files = find(scene_dir, "-name", "*.pov").splitlines()
            for pov_f in pov_files:
                with local.env(POVRAY=bin_name, INSTALL_DIR=self.builddir,
                               OUTPUT_DIR=tmpdir, POVINI=povini):
                    render[tmpdir, "--all", pov_f] & FG(retcode=None)

class OpenSSLGroup(Project):

    """ OpenSSL """

    def __init__(self, exp, name):
        super(OpenSSLGroup, self).__init__(exp, name, "encryption", "openssl")
        self.sourcedir = path.join(config["sourcedir"], "src", "openssl", name)
        self.setup_derived_filenames()
        self.calls_f = path.join(self.builddir, "papi.calls.out")
        self.prof_f = path.join(self.builddir, "papi.profile.out")


class Blowfish(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return Blowfish(exp, "blowfish")
    ProjectFactory.addFactory("Blowfish", Factory())


class Bn(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return Bn(exp, "bn")
    ProjectFactory.addFactory("Bn", Factory())


class Cast(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return Cast(exp, "cast")
    ProjectFactory.addFactory("Cast", Factory())


class DES(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return DES(exp, "des")
    ProjectFactory.addFactory("DES", Factory())


class DSA(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return DSA(exp, "dsa")
    ProjectFactory.addFactory("DSA", Factory())


class ECDSA(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return ECDSA(exp, "ecdsa")
    ProjectFactory.addFactory("ECDSA", Factory())


class HMAC(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return HMAC(exp, "hmac")
    ProjectFactory.addFactory("HMAC", Factory())


class MD5(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return MD5(exp, "md5")
    ProjectFactory.addFactory("MD5", Factory())


class RC4(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return RC4(exp, "rc4")
    ProjectFactory.addFactory("RC4", Factory())


class RSA(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return RSA(exp, "rsa")
    ProjectFactory.addFactory("RSA", Factory())


class SHA1(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return SHA1(exp, "sha1")
    ProjectFactory.addFactory("SHA1", Factory())


class SHA256(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return SHA256(exp, "sha256")
    ProjectFactory.addFactory("SHA256", Factory())


class SHA512(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return SHA512(exp, "sha512")
    ProjectFactory.addFactory("SHA512", Factory())


class SSL(OpenSSLGroup):
    class Factory:
        def create(self, exp):
            return SSL(exp, "ssl")

    def run(self, experiment):
        ssl = experiment["-time", "-cert",
                path.join(self.sourcedir, "server.pem"),
                "-num", 10000, "-named_curve", "c2tnb431r1",
                "-bytes", 20480]
        with local.env(self.builddir):
            ssl["-tls1"] & FG
            ssl["-ssl2"] & FG

    ProjectFactory.addFactory("SSL", Factory())

class OpenSSL(OpenSSLGroup):
    """ OpenSSL benchmark """

    class Factory:
        def create(self, exp):
            return OpenSSL(exp, "openssl")
    ProjectFactory.addFactory("OpenSSL", Factory())

    def run(self, experiment):
        with local.env(OPENSSL_CONF=path.join(self.testdir, "openssl.cnf")):
            certs = path.join(self.testdir, "certs", "demo")
            print certs
            for f in glob(path.join(certs, "*.pem")):
                print f
                super(OpenSSL, self).run(
                    experiment["verify", "-CApath", certs, f])


class Python(PprofGroup):

    """ python benchmarks """

    class Factory:
        def create(self, exp):
            obj = Python(exp, "python", "compilation")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Python", Factory())

    def run(self, experiment):
        testfiles = find(self.testdir, "-name", "*.py").splitlines()
        for f in testfiles:
            with local.env(PYTHONPATH=self.testdir,
                           PYTHONHOME=self.testdir):
                with local.cwd(self.builddir):
                    experiment[f] & FG(retcode=None)


class PolyBenchGroup(Project):

    path_dict = {
        "correlation": "datamining",
        "covariance": "datamining",
        "2mm": "linear-algebra/kernels",
        "3mm": "linear-algebra/kernels",
        "atax": "linear-algebra/kernels",
        "bicg": "linear-algebra/kernels",
        "cholesky": "linear-algebra/kernels",
        "doitgen": "linear-algebra/kernels",
        "gemm": "linear-algebra/kernels",
        "gemver": "linear-algebra/kernels",
        "gesummv": "linear-algebra/kernels",
        "mvt": "linear-algebra/kernels",
        "symm": "linear-algebra/kernels",
        "syr2k": "linear-algebra/kernels",
        "syrk": "linear-algebra/kernels",
        "trisolv": "linear-algebra/kernels",
        "trmm": "linear-algebra/kernels",
        "durbin": "linear-algebra/solvers",
        "dynprog": "linear-algebra/solvers",
        "gramschmidt": "linear-algebra/solvers",
        "lu": "linear-algebra/solvers",
        "ludcmp": "linear-algebra/solvers",
        "floyd-warshall": "medley",
        "reg_detect": "medley",
        "adi": "stencils",
        "fdtd-2d": "stencils",
        "fdtd-apml": "stencils",
        "jacobi-1d-imper": "stencils",
        "jacobi-2d-imper": "stencils",
        "seidel-2d": "stencils"
    }

    def __init__(self, exp, name):
        super(PolyBenchGroup, self).__init__(exp, name, "polybench", "polybench")
        self.sourcedir = path.join(config["sourcedir"],
                                   "polybench", self.path_dict[name], name)
        self.setup_derived_filenames()
        self.calls_f = path.join(self.builddir, "papi.calls.out")
        self.prof_f = path.join(self.builddir, "papi.profile.out")


class Correlation(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Correlation(exp, "correlation")
    ProjectFactory.addFactory("Correlation", Factory())


class Covariance(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Covariance(exp, "covariance")
    ProjectFactory.addFactory("Covariance", Factory())


class TwoMM(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return TwoMM(exp, "2mm")
    ProjectFactory.addFactory("TwoMM", Factory())


class ThreeMM(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return ThreeMM(exp, "3mm")
    ProjectFactory.addFactory("ThreeMM", Factory())


class Atax(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Atax(exp, "atax")
    ProjectFactory.addFactory("Atax", Factory())


class BicG(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return BicG(exp, "bicg")
    ProjectFactory.addFactory("BicG", Factory())


class Cholesky(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Cholesky(exp, "cholesky")
    ProjectFactory.addFactory("Cholesky", Factory())


class Doitgen(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Doitgen(exp, "doitgen")
    ProjectFactory.addFactory("Doitgen", Factory())


class Gemm(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Gemm(exp, "gemm")
    ProjectFactory.addFactory("Gemm", Factory())


class Gemver(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Gemver(exp, "gemver")
    ProjectFactory.addFactory("Gemver", Factory())


class Gesummv(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Gesummv(exp, "gesummv")
    ProjectFactory.addFactory("Gesummv", Factory())


class Mvt(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Mvt(exp, "mvt")
    ProjectFactory.addFactory("Mvt", Factory())


class Symm(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Symm(exp, "symm")
    ProjectFactory.addFactory("Symm", Factory())


class Syr2k(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Syr2k(exp, "syr2k")
    ProjectFactory.addFactory("Syr2k", Factory())


class Syrk(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Syrk(exp, "syrk")
    ProjectFactory.addFactory("Syrk", Factory())


class Trisolv(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Trisolv(exp, "trisolv")
    ProjectFactory.addFactory("Trisolv", Factory())


class Trmm(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Trmm(exp, "trmm")
    ProjectFactory.addFactory("Trmm", Factory())


class Durbin(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Durbin(exp, "durbin")
    ProjectFactory.addFactory("Durbin", Factory())


class Dynprog(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Dynprog(exp, "dynprog")
    ProjectFactory.addFactory("Dynprog", Factory())


class Gramschmidt(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Gramschmidt(exp, "gramschmidt")
    ProjectFactory.addFactory("Gramschmidt", Factory())


class Lu(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Lu(exp, "lu")
    ProjectFactory.addFactory("Lu", Factory())


class LuDCMP(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return LuDCMP(exp, "ludcmp")
    ProjectFactory.addFactory("LuDCMP", Factory())


class FloydWarshall(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return FloydWarshall(exp, "floyd-warshall")
    ProjectFactory.addFactory("FloydWarshall", Factory())


class RegDetect(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return RegDetect(exp, "reg_detect")
    ProjectFactory.addFactory("RegDetect", Factory())


class Adi(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Adi(exp, "adi")
    ProjectFactory.addFactory("Adi", Factory())


class FDTD2D(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return FDTD2D(exp, "fdtd-2d")
    ProjectFactory.addFactory("FDTD2D", Factory())


class FDTDAPML(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return FDTDAPML(exp, "fdtd-apml")
    ProjectFactory.addFactory("FDTDAPML", Factory())


class Jacobi1Dimper(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Jacobi1Dimper(exp, "jacobi-1d-imper")
    ProjectFactory.addFactory("Jacobi1Dimper", Factory())


class Jacobi2Dimper(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Jacobi2Dimper(exp, "jacobi-2d-imper")
    ProjectFactory.addFactory("Jacobi2Dimper", Factory())


class Seidel2D(PolyBenchGroup):
    class Factory:
        def create(self, exp):
            return Seidel2D(exp, "seidel-2d")
    ProjectFactory.addFactory("Seidel2D", Factory())
