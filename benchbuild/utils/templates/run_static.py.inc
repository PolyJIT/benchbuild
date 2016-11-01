#!/usr/bin/env python3
#
from os import path
import sys
import dill

from benchbuild.utils import log
from benchbuild import settings
from plumbum import local

settings.update_env()
log.configure()
log.set_defaults()

RUN_F = "{runf}"
ARGS = sys.argv[1:]
F = None
if path.exists("{blobf}"):
    with local.env(PATH="{path}",
                   LD_LIBRARY_PATH="{ld_lib_path}",
                   BB_CMD=RUN_F + " ".join(ARGS)):
        with open("{blobf}", "rb") as p:
            F = dill.load(p)
        if F is not None:
            RI = F(RUN_F, ARGS,
                   has_stdin=not sys.stdin.isatty(),
                   has_stdout=not sys.stdout.isatty())
            sys.exit(RI.retcode)
        else:
            sys.exit(1)
