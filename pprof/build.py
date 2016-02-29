#!/usr/bin/env python3
"""
Build a LLVM/Clang image with PolyJIT & Polly support.

Many experiments inside the pprof study require these to operate.
This module provides a standard way to get the necessary libraries in one
single image.
"""
import os
from plumbum import cli, local
from plumbum.cmd import mkdir, git, cmake  # pylint: disable=E0401

from pprof.settings import CFG

def clone_or_pull(repo_dict, to_dir):
    """
    Clone or pull a repository and switch to the desired branch.

    If the directory already exists, we will try to du a pull with
    --rebase. In case anything goes wrong, we exit and print a simple
    diagnostic message.

    Args:
        url (str): Where is the remote repository?
        to_dir (str): Where should we clone/update to?
        branch (str): Which branch should we check out? Defaults to the repo's
            master.
    """

    url = repo_dict["url"]
    branch = repo_dict.get("branch")
    commit_hash = repo_dict.get("commit_hash")

    if not os.path.exists(os.path.join(to_dir, ".git/")):
        git_clone = git["clone", url, to_dir, "--recursive", "--depth=1"]
        if branch:
            git_clone = git_clone["--branch", branch]
        git_clone()
    elif not commit_hash:
        # If we haven't specified a commit hash,
        # fetch the latest version.
        with local.cwd(to_dir):
            git("remote", "update")

            locl = git("rev-parse", "@{0}")
            remote = git("rev-parse", "@{u}")
            base = git("merge-base", "@", "@{u}")

            if locl == remote:
                print("{:s} is up-to-date.".format(url))
            elif locl == base:
                git("pull", "--rebase")
                git("submodule", "update")
            elif remote == base:
                print("push required")
                exit(1)
            else:
                print("{:s} has diverged from its remote.".format(to_dir))
                exit(1)

    if commit_hash:
        with local.cwd(to_dir):
            # We only need to do something if we aren't already at the
            # latest commit hash
            current_hash = git("rev-parse", "--verify", "HEAD").rstrip("\n")
            if current_hash != commit_hash:
                # Make sure we have a full history, not just depth 1
                print(("HEAD for repository {:s} is not at configured commit"
                       "hash {:s}, fetching and checking out.".format(
                           url, commit_hash)))
                git("fetch", "--unshallow")
                git("checkout", commit_hash)


def configure_papi(cmake_cmd, root):
    """ Configure cmake with libpapi. """
    llvm_cmake = cmake_cmd
    if os.path.exists(root):
        papi_inc = os.path.join(root, "include")
        papi_lib = os.path.join(root, "lib", "libpapi.so")
        llvm_cmake = llvm_cmake["-DPAPI_INCLUDE_DIR=" + papi_inc]
        llvm_cmake = llvm_cmake["-DPAPI_LIBRARY=" + papi_lib]

    return llvm_cmake


def configure_likwid(cmake_cmd, root):
    """ Configure cmake with likwid. """
    llvm_cmake = cmake_cmd
    if os.path.exists(root):
        likwid_inc = os.path.join(root, "include")
        likwid_lib = os.path.join(root, "lib", "liblikwid.so")
        llvm_cmake = llvm_cmake["-DLIKWID_INCLUDE_DIR=" + likwid_inc]
        llvm_cmake = llvm_cmake["-DLIKWID_LIBRARY=" + likwid_lib]

    return llvm_cmake


def configure_isl(cmake_cmd, root):
    """ Configure cmake with isl. """
    llvm_cmake = cmake_cmd
    if root is not None and os.path.exists(root):
        llvm_cmake = llvm_cmake["-DCMAKE_PREFIX_PATH=" + root]

    return llvm_cmake


def configure_compiler(cmake_cmd, use_gcc):
    """ Configure cmake with the desired compiler. """
    if use_gcc:
        cc_cmd = local["gcc"]
        cpp_cmd = local["g++"]
    else:
        cc_cmd = local["clang"]
        cpp_cmd = local["clang++"]

    if cc_cmd and cpp_cmd:
        llvm_cmake = cmake_cmd
        llvm_cmake = llvm_cmake[
            "-DCMAKE_CXX_COMPILER=" + str(
                cpp_cmd), "-DCMAKE_C_COMPILER=" + str(cc_cmd)]
    return llvm_cmake


class Build(cli.Application):
    """ Build all dependences required to run the pprof study. """

    _use_make = False
    _use_gcc = False
    _num_jobs = None
    _isldir = None
    _likwiddir = None
    _papidir = None
    _builddir = None

    @cli.switch(["--use-make"],
                help="Use make instead of ninja as build system")
    def use_make(self):
        """Use make instead of ninja as build system."""
        self._use_make = True

    @cli.switch(["-j", "--jobs"],
                int,
                help="Number of jobs to use for building")
    def jobs(self, num):
        """Number of jobs to use for building."""
        self._num_jobs = num

    @cli.switch(["--use-gcc"], help="Use gcc to build llvm/clang")
    def use_gcc(self):
        """Use gcc to build llvm/clang."""
        self._use_gcc = True

    @cli.switch(["-B", "--builddir"],
                str,
                help="Where should we build our dependencies?",
                mandatory=True)
    def builddir(self, dirname):
        """Where should we build our dependencies?"""
        self._builddir = os.path.abspath(dirname)

    @cli.switch(["-P", "--papidir"],
                str,
                help="Where is libPAPI?",
                mandatory=True)
    def papidir(self, dirname):
        """Where is libPAPI?"""
        self._papidir = os.path.abspath(dirname)

    @cli.switch(["-L", "--likwiddir"],
                str,
                help="Where is likwid?",
                mandatory=True)
    def likwiddir(self, dirname):
        """Where is likwid?"""
        self._likwiddir = os.path.abspath(dirname)

    @cli.switch(["-I", "--isldir"], str, help="Where is isl?")
    def isldir(self, dirname):
        """Where is isl?"""
        self._isldir = os.path.abspath(dirname)

    def configure_openmp(self, openmp_path):
        """ Configure LLVM/Clang's own OpenMP runtime. """
        with local.cwd(openmp_path):
            builddir = os.path.join(openmp_path, "build")
            if not os.path.exists(builddir):
                mkdir(builddir)
            with local.cwd(builddir):
                cmake_cache = os.path.join(builddir, "CMakeCache.txt")
                install_path = os.path.join(self._builddir, "install")
                openmp_cmake = cmake[
                    "-DCMAKE_INSTALL_PREFIX=" + install_path,
                    "-DCMAKE_BUILD_TYPE=Release",
                    "-DCMAKE_USE_RELATIVE_PATHS=On",
                    "-DLIBOMP_ENABLE_ASSERTIONS=Off"]

                if self._use_make:
                    openmp_cmake = openmp_cmake["-G", "Unix Makefiles"]
                else:
                    openmp_cmake = openmp_cmake["-G", "Ninja"]

                if not os.path.exists(cmake_cache):
                    openmp_cmake = configure_compiler(openmp_cmake,
                                                      use_gcc=False)
                    openmp_cmake = openmp_cmake[openmp_path]
                else:
                    openmp_cmake = openmp_cmake["."]

                openmp_cmake()

    def configure_llvm(self, llvm_path):
        """ Configure LLVM and all subprojects. """
        with local.cwd(llvm_path):
            builddir = os.path.join(llvm_path, "build")
            if not os.path.exists(builddir):
                mkdir(builddir)
            with local.cwd(builddir):
                cmake_cache = os.path.join(builddir, "CMakeCache.txt")
                install_path = os.path.join(self._builddir, "install")
                llvm_cmake = cmake[
                    "-DCMAKE_INSTALL_PREFIX=" + install_path,
                    "-DCMAKE_BUILD_TYPE=Release", "-DBUILD_SHARED_LIBS=Off",
                    "-DCMAKE_USE_RELATIVE_PATHS=On", "-DPOLLY_BUILD_POLLI=On",
                    "-DLLVM_TARGETS_TO_BUILD=X86",
                    "-DLLVM_BINUTILS_INCDIR=/usr/include/",
                    "-DLLVM_ENABLE_PIC=On", "-DLLVM_ENABLE_ASSERTIONS=On",
                    "-DCLANG_DEFAULT_OPENMP_RUNTIME=libomp",
                    "-DCMAKE_CXX_FLAGS_RELEASE='-O3 -DNDEBUG -fno-omit-frame-pointer'"]

                if self._use_make:
                    llvm_cmake = llvm_cmake["-G", "Unix Makefiles"]
                else:
                    llvm_cmake = llvm_cmake["-G", "Ninja"]

                llvm_cmake = configure_papi(llvm_cmake, self._papidir)
                llvm_cmake = configure_likwid(llvm_cmake, self._likwiddir)
                llvm_cmake = configure_isl(llvm_cmake, self._isldir)

                if not os.path.exists(cmake_cache):
                    llvm_cmake = configure_compiler(llvm_cmake, self._use_gcc)
                    llvm_cmake = llvm_cmake[llvm_path]
                else:
                    llvm_cmake = llvm_cmake["."]

                llvm_cmake()

    def main(self):
        print("Building in: {:s}".format(self._builddir))

        if not os.path.exists(self._builddir):
            mkdir(self._builddir)

        llvm_path = os.path.join(self._builddir, "pprof-llvm")
        openmp_path = os.path.join(self._builddir, "openmp-runtime")
        with local.cwd(self._builddir):
            clone_or_pull(CFG['llvm']['dir'], llvm_path)
            tools_path = os.path.join(llvm_path, "tools")
            with local.cwd(tools_path):
                clone_or_pull(CFG['repo']['clang'],
                              os.path.join(tools_path, "clang"))
                clone_or_pull(CFG['repo']['polly'],
                              os.path.join(tools_path, "polly"))
                polli_path = os.path.join(tools_path, "polly", "tools")
                with (local.cwd(polli_path)):
                    clone_or_pull(CFG['repo']['polli'],
                                  os.path.join(polli_path, "polli"))
            clone_or_pull(CFG['repo']['openmp'], openmp_path)

        self.configure_llvm(llvm_path)
        self.configure_openmp(openmp_path)

        build_cmd = None
        if self._use_make:
            build_cmd = local["make"]
        else:
            build_cmd = local["ninja"]

        if self._num_jobs:
            build_cmd = build_cmd["-j", self._num_jobs]

        print("Building LLVM.")
        build_llvm = build_cmd["-C", os.path.join(llvm_path, "build"),
                               "install"]
        build_llvm()
        print("Building OpenMP.")
        build_openmp = build_cmd["-C", os.path.join(openmp_path, "build"),
                                 "install"]
        build_openmp()
