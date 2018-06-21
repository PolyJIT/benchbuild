"""
Settings module for benchbuild.

All settings are stored in a simple dictionary. Each
setting should be modifiable via environment variable.
"""
import os
import uuid
from datetime import datetime

import benchbuild.utils.settings as s

# Initialize the global configuration once.
CFG = s.Configuration(
    "bb",
    node={
        "version": {
            "desc": "Version Number",
            "default": s.__version__,
            "export": False
        },
        "verbosity": {
            "desc": "The verbosity level of the logger. Range: 0-4",
            "default": 0
        },
        "debug": {
            "desc": "Should debug logging be enabled?",
            "default": False
        },
        "config_file": {
            "desc": "Config file path of benchbuild. Not guaranteed to exist.",
            "default": None,
        },
        "src_dir": {
            "desc":
            "source directory of benchbuild. Usually the git repo root dir.",
            "default": os.getcwd()
        },
        "build_dir": {
            "desc":
            "build directory of benchbuild. All intermediate projects will "
            "be placed here",
            "default": os.path.join(os.getcwd(), "results")
        },
        "test_dir": {
            "desc":
            "Additional test inputs, required for (some) run-time tests."
            "These can be obtained from the a different repo. Most "
            "projects don't need it",
            "default": os.path.join(os.getcwd(), "testinputs")
        },
        "tmp_dir": {
            "desc": "Temporary dir. This will be used for caching downloads.",
            "default": os.path.join(os.getcwd(), "tmp")
        },
        "jobs": {
            "desc":
            "Number of jobs that can be used for building and running.",
            "default": str(s.available_cpu_count())
        },
        "experiments": {
            "default": {
                "empty": str(uuid.uuid4())
            },
            "desc": "Dictionary of all experiments we want a defined uuid for."
        },
        "clean": {
            "default": True,
            "desc": "Clean temporary objects, after completion.",
        },
        "experiment_description": {
            "default": str(datetime.now()),
            "export": False
        },
        "regression_prefix": {
            "default": os.path.join("/", "tmp", "benchbuild-regressions")
        },
        "benchbuild_prefix": {
            "default": os.getcwd()
        },
        "benchbuild_ebuild": {
            "default": ""
        },
        "cleanup_paths": {
            "default": [],
            "desc":
            "List of existing paths that benchbuild should delete in addition "
            "to the default cleanup steps.",
            "export": False
        },
        "sequence": {
            "desc": "The name of the sequence that should be used for "
                    "preoptimization.",
            "default": "no_preperation"
        }
    })

CFG["compiler"] = {
    "c": {
        "desc": "The C compiler we should use.",
        "default": "clang"
    },
    "cxx": {
        "desc": "The C++ compiler we should use.",
        "default": "clang++"
    }
}

CFG["unionfs"] = {
    "enable": {
        "default": True,
        "desc": "Wrap all project operations in a unionfs filesystem."
    },
    "base_dir": {
        "default": './base',
        "desc": 'Path of the unpacked container.'
    },
    "image": {
        "default": './image',
        "desc": 'Name of the image directory'
    },
    "image_prefix": {
        "default": None,
        "desc": "Prefix for the unionfs image directory."
    }
}

CFG["env"] = {
    "ld_library_path": {
        "desc": "LD_LIBRARY_PATH for benchbuild.",
        "default": []
    },
    "path": {
        "desc": "PATH for benchbuild.",
        "default": []
    }
}

CFG['db'] = {
    "connect_string": {
        "desc": "sqlalchemy connect string",
        "default": "postgresql+psycopg2://"
                   "benchbuild:benchbuild@localhost:5432/benchbuild"
    },
    "rollback": {
        "desc": "Rollback all operations after benchbuild completes.",
        "default": False
    },
    "create_functions": {
        "default": False,
        "desc": "Should we recreate our SQL functions from scratch?"
    }
}

CFG['gentoo'] = {
    "autotest_lang": {
        "default": "",
        "desc": "Language filter for ebuilds, like C or C++."
    },
    "autotest_use": {
        "default": "",
        "desc":
        "USE filter for ebuilds. Filters packages without the given use flags."
    },
    "autotest_loc": {
        "default": "/tmp/gentoo-autotest",
        "desc": "Location for the list of auto generated ebuilds."
    },
    "http_proxy": {
        "default": None,
        "desc": "HTTP Proxy to use for downloads."
    },
    "rsync_proxy": {
        "default": None,
        "desc": "RSYNC Proxy to use for downloads."
    },
    "ftp_proxy": {
        "default": None,
        "desc": "FTP Proxy to use for downloads."
    }
}

CFG["slurm"] = {
    "account": {
        "desc": "The SLURM account to use by default.",
        "default": "cl"
    },
    "partition": {
        "desc": "The SLURM partition to use by default.",
        "default": "chimaira"
    },
    "script": {
        "desc":
        "Name of the script that can be passed to SLURM. Used by external "
        "tools.",
        "default": "slurm.sh"
    },
    "cpus_per_task": {
        "desc":
        "Number of CPUs that should be requested from SLURM. Used by external "
        "tools.",
        "default": 10
    },
    "node_dir": {
        "desc":
        "Node directory, when executing on a cluster node. This is not "
        "used by benchbuild directly, but by external scripts.",
        "default": os.path.join(os.getcwd(), "results")
    },
    "timelimit": {
        "desc": "The timelimit we want to give to a job",
        "default": "12:00:00"
    },
    "exclusive": {
        "desc":
        "Shall we reserve a node exclusively, or share it with others?",
        "default": True
    },
    "multithread": {
        "desc": "Hint SLURM to allow multithreading. (--hint=nomultithread)",
        "default": False
    },
    "turbo": {
        "desc": "Disable Intel Turbo Boost via SLURM. (--pstate-turbo=off)",
        "default": False
    },
    "logs": {
        "desc": "Location the SLURM logs will be stored",
        "default": "slurm.log"
    },
    "nice": {
        "desc": "Add a niceness value on our priority",
        "default": 0
    },
    "nice_clean": {
        "desc": "Add a niceness value on our cleanup job priority",
        "default": 2500
    },
    "max_running": {
        "desc": "Limit the number of concurrent running array jobs",
        "default": 0
    },
    "node_image": {
        "desc": "Path to the archive we want on each cluster node.",
        "default": os.path.join(os.path.curdir, "llvm.tar.gz")
    },
    "extra_log": {
        "desc": "Extra log file to be managed by SLURM",
        "default": "/tmp/.slurm"
    }
}

CFG["perf"] = {
    "config": {
        "default": None,
        "desc": "A configuration for the pollyperformance experiment."
    }
}

CFG["cs"] = {
    "components": {
        "default": None,
        "desc": "List of filters for compilestats components."
    },
    "names": {
        "default": None,
        "desc": "List of filters for compilestats names."
    }
}

CFG["uchroot"] = {
    "repo": {
        "default": "https://github.com/PolyJIT/erlent.git/",
        "desc": "GIT Repo URL for erlent."
    }
}

CFG["plugins"] = {
    "autoload": {
        "default": True,
        "desc": "Should automatic load of plugins be enabled?"
    },
    "reports": {
        "default": [
            "benchbuild.reports.compilestats",
            "benchbuild.reports.raw",
            "benchbuild.reports.status"
        ],
        "desc": "Report plugins."
    },
    "experiments": {
        "default": [
            "benchbuild.experiments.raw",
            "benchbuild.experiments.compilestats",
            "benchbuild.experiments.polyjit",
            "benchbuild.experiments.empty",
            "benchbuild.experiments.papi",
            "benchbuild.experiments.pjtest",
            "benchbuild.experiments.pj_raw",
            "benchbuild.experiments.pj_likwid",
            "benchbuild.experiments.pj_collect",
            "benchbuild.experiments.pj_cs",
            "benchbuild.experiments.pj_papi",
            "benchbuild.experiments.pj_sequence",
            "benchbuild.experiments.pgo",
            "benchbuild.experiments.pollytest",
            "benchbuild.experiments.profileScopDetection",
            "benchbuild.experiments.mse",
            "benchbuild.experiments.ijpp"
        ],
        "desc": "The experiment plugins we know about."
    },
    "projects": {
        "default": [
            "benchbuild.projects.gentoo",
            "benchbuild.projects.lnt.lnt",
            "benchbuild.projects.polybench.polybench",
            "benchbuild.projects.polybench.polybench-mod",
            "benchbuild.projects.benchbuild.bots",
            "benchbuild.projects.benchbuild.bzip2",
            "benchbuild.projects.benchbuild.ccrypt",
            "benchbuild.projects.benchbuild.crafty",
            "benchbuild.projects.benchbuild.crocopat",
            "benchbuild.projects.benchbuild.ffmpeg",
            "benchbuild.projects.benchbuild.gzip",
            "benchbuild.projects.benchbuild.js",
            "benchbuild.projects.benchbuild.lammps",
            "benchbuild.projects.benchbuild.lapack",
            "benchbuild.projects.benchbuild.leveldb",
            "benchbuild.projects.benchbuild.linpack",
            "benchbuild.projects.benchbuild.lulesh",
            "benchbuild.projects.benchbuild.luleshomp",
            "benchbuild.projects.benchbuild.mcrypt",
            "benchbuild.projects.benchbuild.minisat",
            "benchbuild.projects.benchbuild.openssl",
            "benchbuild.projects.benchbuild.povray",
            "benchbuild.projects.benchbuild.python",
            "benchbuild.projects.benchbuild.rasdaman",
            "benchbuild.projects.benchbuild.ruby",
            "benchbuild.projects.benchbuild.sdcc",
            "benchbuild.projects.benchbuild.sevenz",
            "benchbuild.projects.benchbuild.sqlite3",
            "benchbuild.projects.benchbuild.tcc",
            "benchbuild.projects.benchbuild.x264",
            "benchbuild.projects.benchbuild.xz",
            "benchbuild.projects.apollo.scimark",
            "benchbuild.projects.apollo.rodinia",
            "benchbuild.projects.test.test"
        ],
        "desc": "The project plugins we know about."
    }
}

CFG["container"] = {
    "input": {
        "default": "container.tar.bz2",
        "desc": "Input container file/folder."
    },
    "output": {
        "default": "container-out.tar.bz2",
        "desc": "Output container file."
    },
    "mounts": {
        "default": [],
        "desc": "List of paths that will be mounted inside the container."
    },
    "prefixes": {
        "default": [],
        "desc": "List of paths that will be treated as an "
                "existing prefix inside a container."
    },
    "shell": {
        "default": "/bin/bash",
        "desc": "Command string that should be used as shell command."
    },
    "known": {
        "default": [],
        "desc": "List of known containers. Format: "
                "[{ 'path': <path>,"
                "   'hash': <hash> }]"
    },
    "images": {
        "default": {
            "gentoo": "gentoo.tar.bz2",
            "ubuntu": "ubuntu.tar.bz2"
        }
    },
    "prefered": {
        "default": [],
        "desc": "List of containers of which the project can chose from."
                "Format:"
                "[{ 'path': <path> }]"
    },
    "strategy": {
        "polyjit": {
            "sync": {"default": True, "desc": "Update portage tree?"},
            "upgrade": {"default": True, "desc": "Upgrade all packages?"},
            "packages": {
                "default": [
                    {"name": "sys-devel/gcc:5.4.0", "env": {
                        "ACCEPT_KEYWORDS": "~amd64",
                        "USE": "-filecaps"
                    }},
                    {"name": "dev-db/postgresql:9.5", "env": {}},
                    {"name": "dev-python/pip", "env": {}},
                    {"name": "net-misc/curl", "env": {}},
                    {"name": "sys-apps/likwid", "env": {
                        "USE": "-filecaps",
                        "ACCEPT_KEYWORDS": "~amd64"
                    }},
                    {"name": "dev-libs/libpfm", "env": {
                        "USE": "static-libs",
                        "ACCEPT_KEYWORDS": "~amd64"
                    }},
                    {"name": "sys-process/time", "env": {}},
                    {"name": "=dev-util/boost-build-1.58.0", "env": {
                        "ACCEPT_KEYWORDS": "~amd64"
                    }},
                    {"name": "=dev-libs/boost-1.62-r1", "env": {
                        "ACCEPT_KEYWORDS": "~amd64"
                    }},
                    {"name": "dev-libs/libpqxx", "env": {}},
                    {"name": "dev-lang/python-3.5.3", "env": {
                        "ACCEPT_KEYWORDS": "~amd64"
                    }},
                    {"name": "dev-python/dill", "env": {
                        "ACCEPT_KEYWORDS": "~amd64"
                    }}
                ],
                "desc": "A list of gentoo package atoms that should be merged."
            }
        }
    }
}

s.setup_config(CFG)
s.update_env(CFG)
