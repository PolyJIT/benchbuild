from plumbum import cli
from pprof.driver import PollyProfiling

import os.path

@PollyProfiling.subcommand("config")
class PprofGenConfig(cli.Application):
    """ Generate a default configuration that can be edited in a text editor. """

    _outpath = "./pprof_config.py"

    @cli.switch(["-o"], str, help="Where to write the default config file? File type is *.py")
    def set_output(self, dirname):
        self._outpath = dirname

    def main(self):
        import settings

        self._outpath = os.path.abspath(self._outpath)

        if os.path.exists(self._outpath):
            if not query_yes_no("File " + self._outpath + " exists already. Overwrite?", "no"):
                exit(1)

        with open(self._outpath, "w") as outfile:
            outfile.write("config = {}\n\n\n")

            for setting in settings.config_metadata:
                outfile.write("## " + setting["name"] + "\n")
                #outfile.write("# " + setting.desc)
                outfile.write("# Default value: " + repr(setting["default"]) + "\n")
                outfile.write("#config[" + repr(setting["name"]) + "] = \n")
                outfile.write("\n\n")

        print("Configuration file has been written to " + self._outpath)

import sys

# Taken from the following recipe: http://code.activestate.com/recipes/577058/
def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
