#!/usr/bin/env python

from plumbum import local, cli
from plumbum.cmd import git

from pprof.settings import config
import os

def getLLVMVersion():
    if config["llvm-srcdir"] is not None:
      to_dir = os.path.join(config["llvm-srcdir"],".git/")
      with local.cwd(to_dir):
          return git("rev-parse", "HEAD")
    return ""

def getClangVersion():
    if config["llvm-srcdir"] is not None:
      to_dir = os.path.join(config["llvm-srcdir"],"tools/clang/.git/")
      with local.cwd(to_dir):
          return git("rev-parse", "HEAD")
    return ""

def getPollyVersion():
    if config["llvm-srcdir"] is not None:
      to_dir = os.path.join(config["llvm-srcdir"],"tools/polly/.git/")
      with local.cwd(to_dir):
         return git("rev-parse", "HEAD")
    return ""

def getPolliVersion():
    if config["llvm-srcdir"] is not None:
      to_dir = os.path.join(config["llvm-srcdir"],"tools/polly/tools/polli/.git/")
      with local.cwd(to_dir):
        return git("rev-parse", "HEAD")
    return ""
