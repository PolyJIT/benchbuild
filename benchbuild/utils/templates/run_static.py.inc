#!/usr/bin/env python3
#
from benchbuild.utils import log
from benchbuild import settings
from plumbum import local
from os import path
import sys
import dill

settings.update_env()
log.configure()
log.set_defaults()

run_f = "{runf}"
args = sys.argv[1:]
f = None
if path.exists("{blobf}"):
    with local.env(PATH="{path}",
                   LD_LIBRARY_PATH="{ld_lib_path}",
                   BB_CMD=run_f + " ".join(args)):
        with open("{blobf}", "rb") as p:
            f = dill.load(p)
        if f is not None:
            if not sys.stdin.isatty():
                f(run_f, args, has_stdin=True)
            else:
                f(run_f, args)
        else:
            sys.exit(1)
