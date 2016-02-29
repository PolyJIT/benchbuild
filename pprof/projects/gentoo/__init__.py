from pprof.settings import CFG
CFG['gentoo'] = {
    "autotest-lang": {
        "default": "C, C++",
        "desc": "Language filter for ebuilds."
    },
    "autotest-loc": {
        "default": "/tmp/gentoo-autotest",
        "desc": "Location for the list of auto generated ebuilds."
    }
}

from . import gentoo
from . import bzip2
from . import gzip
from . import sevenz
from . import xz
from . import postgresql
from . import lammps
from . import x264
from . import crafty
from . import portage_gen
from . import info

# Dynamically create projects from the gentoo ebuild index.
if CFG['gentoo']['gentoo-autotest-loc'].value():
    pass
