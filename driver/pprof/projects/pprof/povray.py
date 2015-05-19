#!/usr/bin/evn python
# encoding: utf-8

from pprof.project import ProjectFactory, log_with, log
from pprof.settings import config
from group import PprofGroup

from os import path
from plumbum import FG, local
from plumbum.cmd import cp, echo, chmod, find

class Povray(PprofGroup):

    """ povray benchmark """

    class Factory:
        def create(self, exp):
            obj = Povray(exp, "povray", "multimedia")
            obj.calls_f = path.join(obj.builddir, "papi.calls.out")
            obj.prof_f = path.join(obj.builddir, "papi.profile.out")
            return obj
    ProjectFactory.addFactory("Povray", Factory())

    src_uri = "https://github.com/POV-Ray/povray"
    src_dir = "povray"
    def download(self):
        from pprof.utils.downloader import Git
        from plumbum.cmd import git
        with local.cwd(self.builddir):
            Git(self.src_uri, self.src_dir)

    def configure(self):
        povray_dir = path.join(self.builddir, self.src_dir)
        with local.cwd(path.join(povray_dir, "unix")):
            prebuild_sh = local["./prebuild.sh"]
            prebuild_sh()

        with local.cwd(povray_dir):
            configure = local["./configure"]
            with local.env(COMPILED_BY="PPROF <no@mail.nono>"):
                configure()

    def build(self):
        from plumbum.cmd import make, ln
        povray_dir = path.join(self.builddir, self.src_dir)

        with local.cwd(povray_dir):
            make & FG

        ln("-sf", path.join(povray_dir, "bin", "povray"), self.bin_f)

    def prepare(self):
        super(Povray, self).prepare()
        cp["-ar", path.join(self.testdir, "cfg"), self.builddir] & FG
        cp["-ar", path.join(self.testdir, "etc"), self.builddir] & FG
        cp["-ar", path.join(self.testdir, "scenes"), self.builddir] & FG
        cp["-ar", path.join(self.testdir, "share"), self.builddir] & FG
        cp["-ar", path.join(self.testdir, "test"), self.builddir] & FG

    def run_tests(self, experiment):
        tmpdir = path.join(self.builddir, "tmp")
        povini = path.join(self.builddir, "cfg", ".povray", "3.6", "povray.ini")

        mkdir(tmpdir, retcode=None)
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
