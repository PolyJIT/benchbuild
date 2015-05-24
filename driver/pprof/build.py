#!/usr/bin/env python
# encoding: utf-8

from plumbum import cli, local, FG
from pprof import PollyProfiling
from settings import config

llvm_url = "http://llvm.org/git/llvm.git"
polly_url = "http://github.com/simbuerg/polly.git"
clang_url = "http://llvm.org/git/clang.git"
polli_url = "http://github.com/simbuerg/polli.git"

from plumbum.cmd import mkdir
import sys
import os
import logging
log = logging.getLogger()

git = None
cmake = None


@PollyProfiling.subcommand("build")
class Build(cli.Application):

    """ Build all dependences required to run the pprof study """

    _use_make = False
    _use_gcc = False
    _num_jobs = None

    def setup_commands(self):
        global git, cmake
        git = local["git"]
        cmake = local["cmake"]

    @cli.switch(
        ["--use-make"],
        help="Use make instead of ninja as build system")
    def use_make(self):
        self._use_make = True

    @cli.switch(
        ["-j", "--jobs"], int, help="Number of jobs to use for building")
    def jobs(self, num):
        self._num_jobs = num

    @cli.switch(["--use-gcc"], help="Use gcc to build llvm/clang")
    def use_gcc(self):
        self._use_gcc = True

    @cli.switch(
        ["-B", "--builddir"], str,
        help="Where should we build our dependencies?")
    def builddir(self, dirname):
        self._builddir = dirname

    @cli.switch(["-P", "--papidir"], str, help="Where is libPAPI?")
    def papidir(self, dirname):
        self._papidir = dirname

    @cli.switch(["-L", "--likwiddir"], str, help="Where is likwid?")
    def likwiddir(self, dirname):
        self._likwiddir = dirname

    @cli.switch(["-I", "--isldir"], str, help="Where is isl?")
    def isldir(self, dirname):
        self._isldir = dirname

    def clone_or_pull(self, url, to_dir, branch=None):
        if not os.path.exists(os.path.join(to_dir, ".git/")):
            git_clone = git["clone", url, to_dir, "--recursive", "--depth=1"]
            if branch:
                git_clone = git_clone["--branch", branch]
            git_clone & FG
        else:
            with local.cwd(to_dir):
                git["remote", "update"] & FG

                locl = git("rev-parse", "@{0}")
                remote = git("rev-parse", "@{u}")
                base = git("merge-base", "@", "@{u}")

                if locl == remote:
                    log.info(url + " is up-to-date.")
                elif locl == base:
                    git["pull", "--rebase"] & FG
                    git["submodule", "update"] & FG
                elif remote == base:
                    log.error("push required")
                    exit(1)
                else:
                    log.error(to_dir + "has diverged from its remote.")
                    exit(1)

    def configure_llvm(self, llvm_path):
        with local.cwd(llvm_path):
            builddir = os.path.join(llvm_path, "build")
            if not os.path.exists(builddir):
                mkdir(builddir)
            with local.cwd(builddir):
                cmake_cache = os.path.join(builddir, "CMakeCache.txt")
                install_path = os.path.join(self._builddir, "install")
                llvm_cmake = cmake[
                    "-DCMAKE_INSTALL_PREFIX="+install_path,
                    "-DCMAKE_BUILD_TYPE=Release",
                    "-DBUILD_SHARED_LIBS=On",
                    "-DCMAKE_USE_RELATIVE_PATHS=On",
                    "-DPOLLY_BUILD_POLLI=On",
                    "-DLLVM_TARGETS_TO_BUILD=X86",
                    "-DLLVM_BINUTILS_INCDIR=/usr/include/",
                    "-DLLVM_ENABLE_PIC=On"]

                if self._use_make:
                    llvm_cmake = llvm_cmake["-G", "Unix Makefiles"]
                else:
                    llvm_cmake = llvm_cmake["-G", "Ninja"]

                if os.path.exists(self._papidir):
                    papi_inc = os.path.join(self._papidir, "include")
                    papi_lib = os.path.join(self._papidir, "lib", "libpapi.so")
                    llvm_cmake = llvm_cmake["-DPAPI_INCLUDE_DIR="+papi_inc]
                    llvm_cmake = llvm_cmake["-DPAPI_LIBRARY="+papi_lib]

                if os.path.exists(self._likwiddir):
                    likwid_inc = os.path.join(self._likwiddir, "include")
                    likwid_lib = os.path.join(
                        self._likwiddir,
                        "lib",
                        "liblikwid.so")
                    llvm_cmake = llvm_cmake["-DLIKWID_INCLUDE_DIR="+likwid_inc]
                    llvm_cmake = llvm_cmake["-DLIKWID_LIBRARY="+likwid_lib]

                if os.path.exists(self._isldir):
                    llvm_cmake = llvm_cmake["-DCMAKE_PREFIX_PATH="+self._isldir]

                if not os.path.exists(cmake_cache):
                    cc = None
                    cpp = None
                    if self._use_gcc:
                        cc = local["gcc"]
                        cpp = local["g++"]
                    else:
                        cc = local["clang"]
                        cpp = local["clang++"]

                    if cc and cpp:
                        llvm_cmake = llvm_cmake[
                            "-DCMAKE_CXX_COMPILER=" + str(cpp),
                            "-DCMAKE_C_COMPILER=" + str(cc)]
                    llvm_cmake = llvm_cmake[llvm_path]
                else:
                    llvm_cmake = llvm_cmake["."]

                llvm_cmake & FG

    def main(self):
        log.info("Building in: " + self._builddir)
        self.setup_commands()

        if not os.path.exists(self._builddir):
            mkdir(self._builddir)

        llvm_path = os.path.join(self._builddir, "pprof-llvm")
        with local.cwd(self._builddir):
            self.clone_or_pull(llvm_url, llvm_path)
            tools_path = os.path.join(llvm_path, "tools")
            with local.cwd(tools_path):
                self.clone_or_pull(clang_url, os.path.join(tools_path, "clang"))
                self.clone_or_pull(
                    polly_url,
                    os.path.join(
                        tools_path,
                        "polly"),
                    "devel")
                polli_path = os.path.join(tools_path, "polly", "tools")
                with (local.cwd(polli_path)):
                    self.clone_or_pull(
                        polli_url,
                        os.path.join(
                            polli_path,
                            "polli"))

        self.configure_llvm(llvm_path)

        build_cmd = None
        if self._use_make:
            build_cmd = local["make"]
        else:
            build_cmd = local["ninja"]

        if self._num_jobs:
            build_cmd = build_cmd["-j", self._num_jobs]

        build_cmd["-C"+os.path.join(llvm_path, "build"), "install"] & FG
