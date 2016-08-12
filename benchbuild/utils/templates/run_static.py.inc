#!/usr/bin/env python3
#
from plumbum import cli, local
from os import path, getenv
from benchbuild.utils import log
from benchbuild import settings
import sys
import dill

settings.update_env()
log.configure()
log.set_defaults()

run_f = "{runf}"
args = sys.argv[1:]
f = None
if path.exists("{blobf}"):
    with local.env(BB_DB_HOST="{db_host}",
                   BB_DB_PORT="{db_port}",
                   BB_DB_NAME="{db_name}",
                   BB_DB_USER="{db_user}",
                   BB_DB_PASS="{db_pass}",
                   PATH="{path}",
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
