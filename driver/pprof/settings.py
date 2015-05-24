import os

config = {
    "sourcedir"       : os.getcwd(),
    "builddir"        : os.path.join(os.getcwd(), "results"),
    "testdir"         : os.path.join(os.getcwd(), "./testinputs"),
    "llvmdir"         : os.path.join(os.getcwd(), "./install"),
    "likwiddir"       : os.path.join(os.getcwd(), "/usr"),
    "path"            : os.environ["PATH"],
    "ld_library_path" : os.environ["LD_LIBRARY_PATH"]
}
