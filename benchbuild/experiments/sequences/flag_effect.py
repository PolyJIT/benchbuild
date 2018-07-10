#!/usr/bin/env python
"""This module supplies functionality to test the effect of adding a flag to a
custom sequence on the fitness value of the custom sequence.
"""
import getopt
import sys
import logging

import benchbuild.experiments.sequences.polly_stats as polly_stats
import pprof_utilities


__author__ = "Christoph Woller"
__credits__ = ["Christoph Woller"]
__maintainer__ = "Christoph Woller"
__email__ = "wollerch@fim.uni-passau.de"

# Where is the file located that contains the program's sequence that should
#  be shortened?
FILE_PATH = '<filepath>'

# What is the suffix of the file that contains the program's sequence that
# should be shortened?
FILE_SUFFIX = '.heuristic-compilestats.raw'


def test_effect_of_flag(program, flag, prepending, both, file_path, file_name):
    """Checks the effect of adding a flag to a sequence which does not contain
    this flag.

    Args:
        program (string): the name of the program the effect of the sequence
            should be tested for.
        flag (string): the flag whose effect should be tested.
        prepending (boolean): true if the flag should be prepended; false if
            the flag should be appended.
        both (boolean): true if the flag should be appended and prepended;
            false otherwise.
        file_path (string): the path to the file that contains the sequence for
            the program.
        file_name (string): the name of the file that contains the sequence for
            the program.
    """
    log = logging.getLogger(__name__)
    sequence = pprof_utilities.read_sequence(file_path, file_name)

    if sequence and flag not in sequence:
        log.info("Test effect of Flag: %s", flag)
        sequence_with_flag = list(sequence)

        if both:
            log.info("Stats of sequence with appended and prepended flag...")
            sequence_with_flag.insert(0, flag)
            sequence_with_flag.append(flag)
        else:
            if prepending:
                log.info("Stats of sequence with prepended flag...")
                sequence_with_flag.insert(0, flag)
            else:
                log.info("Stats of sequence with appended flag...")
                sequence_with_flag.append(flag)

        polly_stats.detect_scops(sequence_with_flag, program + '.bc')


def __usage():
    """Prints out the usage of this python script."""
    log = logging.getLogger(__name__)
    log.warning("Wrong usage!")
    log.wraning("You have to specify a flag whose effect should be tested!")
    log.warning(
        "Usage: flag_effect.py -f [--flag=] FLAG_NAME [-p/--prepending]")


def main(argv):
    """Calls the test_effect_of_flag method with the required arguments. If
    the required arguments are not provided by the user, the usage
    description of this script is printed out.
    """
    try:
        opts, args = getopt.getopt(argv, 'hpbf:',
                                   ['help', 'prepending', 'flag=', 'folder=',
                                    'both'])
    except getopt.GetoptError:
        __usage()
        sys.exit(2)

    prepending = None
    file_name = None
    folder = None
    flag = None
    both = False

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            __usage()
            sys.exit()
        elif opt == '--folder':
            folder = arg
        elif opt == '--both':
            both = True
        elif opt in ('-f', '--flag'):
            if args:
                flag = arg
                file_name = str(args[0]) + FILE_SUFFIX
            else:
                __usage()
        elif opt in ('-p', '--prepending'):
            prepending = True

    if flag is not None and prepending is not None and file_name is not None:
        if folder is not None:
            file_name = folder + '/' + file_name

        test_effect_of_flag(args[0], flag, prepending, both, FILE_PATH,
                            file_name)


if __name__ == '__main__':
    main(sys.argv[1:])
