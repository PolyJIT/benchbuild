#!/usr/bin/env python
# encoding: utf-8

from pprof.project import Project, ProjectFactory
from plumbum import local

class GentooGroup(Project):

  """
  Gentoo ProjectGroup for running the gentoo test suite.

  The following packages are required to run GentooGroup
  * fakeroot

  """

  def __init__(self, exp, name):
    super(GentooGroup, self).__init__(exp, name, "gentoo", "gentoo")

  src_dir = "gentoo"
  src_file = src_dir + ".tar.bz2"
  # TODO always new stage3
  src_uri = "http://distfiles.gentoo.org/releases/amd64/autobuilds/20151022/stage3-amd64-20151022.tar.bz2"
  test_suite_dir = "TODO"
  test_suite_uri = "TODO"

  def download(self):
    from pprof.utils.downloader import Wget
    from plumbum.cmd import virtualenv
    with local.cwd(self.builddir):
      Wget(self.src_uri, self.src_file)

      from plumbum.cmd import tar, fakeroot
      from plumbum import FG
      fakeroot["tar", "xfj", self.src_file]& FG

  def configure(self):
    from plumbum.cmd import mkdir, rm
    with local.cwd(self.builddir):
      with open("etc/portage/make.conf", 'w') as makeconf:
        lines = '''# These settings were set by the catalyst build script that automatically
# built this stage.
# Please consult /usr/share/portage/config/make.conf.example for a more
# detailed example.
CFLAGS="-O2 -pipe"
CXXFLAGS="${CFLAGS}"

FEATURES="-sandbox -usersandbox fakeroot -usersync -xattr"

# set compiler
CC="/usr/bin/gcc"
CXX="/usr/bin/gcc++"
#CC="/usr/bin/clang"
#CXX="/usr/bin/clang++"

PORTAGE_USERNAME = "root"
PORTAGE_GRPNAME = "root"
PORTAGE_INST_GID = 0
PORTAGE_INST_UID = 0

# WARNING: Changing your CHOST is not something that should be done lightly.
# Please consult http://www.gentoo.org/doc/en/change-chost.xml before changing.
CHOST="x86_64-pc-linux-gnu"
# These are the USE flags that were used in addition to what is provided by the
# profile used for building.
USE="bindist mmx sse sse2"
PORTDIR="/usr/portage"
DISTDIR="${PORTDIR}/distfiles"
PKGDIR="${PORTDIR}/packages"'''
        makeconf.write(lines)
        # cp jit into gentoo

class Eix(GentooGroup):

  class Factory:

      def create(self, exp):
          return Eix(exp, "eix")
  ProjectFactory.addFactory("Eix", Factory())

  def build(self):
    # cd into chroot
    with local.cwd(self.builddir):
        print "\n"
        print self.builddir
        print local.env["PWD"]
    pass

  def run_tests(self, experiment):
    pass

