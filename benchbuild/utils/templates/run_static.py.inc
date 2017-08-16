#!{python}
#
from os import path
import sys
import dill

from benchbuild.utils import log
from benchbuild.utils.run import exit_code_from_run_infos
from benchbuild import settings
from plumbum import local

settings.update_env()
log.configure()
log.set_defaults()

RUN_F = local["{runf}"]
ARGS = sys.argv[1:]
F = None
if path.exists("{blobf}"):
    with local.env(PATH="{path}",
                   LD_LIBRARY_PATH="{ld_lib_path}",
                   BB_CMD=str(RUN_F) + " ".join(ARGS)):
        with open("{blobf}", "rb") as p:
            F = dill.load(p)
        if F is not None:
            RI = F(RUN_F, ARGS,
                   has_stdin=not sys.stdin.isatty(),
                   has_stdout=not sys.stdout.isatty())
            sys.exit(exit_code_from_run_infos(RI))
        else:
            sys.exit(1)
