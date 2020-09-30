"""
User interface helpers for benchbuild.
"""
import logging
import os
import sys

LOG = logging.getLogger(__name__)


# Taken from the following recipe: http://code.activestate.com/recipes/577058/
def query_yes_no(question, default="yes"):
    """
    Ask a yes/no question via raw_input() and return their answer.

    Args:
        question (str): Question hat is presented to the user.
        default (str): The presumed answer, if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    Returns (boolean):
        True, if 'yes', False otherwise.
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '{0!s}'".format(default))

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        if choice in valid:
            return valid[choice]
        sys.stdout.write(
            "Please respond with 'yes' or 'no' "
            "(or 'y' or 'n').\n"
        )


def ask(
    question: str,
    default_answer: bool = False,
    default_answer_str: str = "no"
) -> bool:
    """
    Ask for user input.

    This asks a yes/no question with a preset default.
    You can bypass the user-input and fetch the default answer, if
    you set

    Args:
        question: The question to ask on stdout.
        default_answer: The default value to return.
        default_answer_str:
            The default answer string that we present to the user.
    """
    response = default_answer

    def should_ignore_tty():
        """
        Check, if we want to ignore an opened tty result.
        """
        ret_to_bool = {"yes": True, "no": False, "true": True, "false": False}
        envs = [os.getenv("CI", default="no"), os.getenv("TEST", default="no")]
        vals = [ret_to_bool[val] for val in envs if val in ret_to_bool]
        return any(vals)

    ignore_stdin_istty = should_ignore_tty()
    has_tty = sys.stdin.isatty() and not ignore_stdin_istty
    if has_tty:
        response = query_yes_no(question, default_answer_str)
    else:
        LOG.debug("NoTTY: %s -> %s", question, response)

    return response
