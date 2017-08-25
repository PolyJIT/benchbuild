#!{python}
#
from os import path
import logging
import sys
import dill

from benchbuild.utils import log
from benchbuild.utils.run import exit_code_from_run_infos
from benchbuild import settings
from plumbum import local, FG

settings.update_env()
log.configure()
log.set_defaults()

LOG = logging.getLogger(__name__)
RUN_F = local["{runf}"]
ARGS = sys.argv[1:]
F = None

with local.env(PATH="{path}",
               LD_LIBRARY_PATH="{ld_lib_path}",
               BB_CMD=str(RUN_F) + " ".join(ARGS)):
    if not path.exists("{blobf}"):
        LOG.info("No measurement blob found at %s", "{blobf}")
        RETCODE, _, _ = RUN_F[ARGS] & FG
        sys.exit(RETCODE)

    with open("{blobf}", "rb") as p:
        F = dill.load(p)
    if F is not None:
        RI = F(RUN_F, ARGS,
               has_stdin=not sys.stdin.isatty(),
               has_stdout=not sys.stdout.isatty())
        sys.exit(exit_code_from_run_infos(RI))
    else:
        LOG.error("Unable to load measurement blob %s", "{blobf}")
        RETCODE, _, _ = RUN_F[ARGS] & FG
        sys.exit(RETCODE)
