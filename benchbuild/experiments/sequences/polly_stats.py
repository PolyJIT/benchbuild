#!/usr/bin/env python
"""This module supplies utility functions that are required to retrieve
information from calls of the LLVM opt tool.
"""
import os
from benchbuild.utils.compiler import compiler

__author__ = "Christoph Woller"
__credits__ = ["Christoph Woller"]
__maintainer__ = "Christoph Woller"
__email__ = "wollerch@fim.uni-passau.de"

# Where is Polly?
POLLY = '-load=/home/wollerch/llvm/install/llvm/lib/LLVMPolly.so'
OPT_CALL = ['/home/wollerch/llvm/install/llvm/bin/opt', '-strip-debug', POLLY]
TEST_POLLY = '-load=/Users/c-Mac/Applications/llvm/install/llvm/lib' \
             '/LLVMPolly.so'
TEST_OPT_CALL = ['/Users/c-Mac/Applications/llvm/install/llvm/bin/opt',
                 '-strip-debug', TEST_POLLY]

# Flags required to get detection result
STATS_FLAGS = ['-polly-detect', '-stats']


def detect_scops(opt_flags, program):
    """Calls the opt tool (with Polly) to detect SCoPs in specified program
    and prints out the results of the detection.

    Args:
        opt_flags (list[string]): the flags opt should be called with.
        program (string): the application opt should run the detection on.
    """
    command = OPT_CALL + opt_flags + STATS_FLAGS + [program]
    print('Opt call: ' + str(command))
    fnull = open(os.devnull, 'w')
    p = compiler(CFG["compiler"]["cxx"].value())
    _, stderr = p.communicate()
    output = stderr.splitlines()

    for line in output:
        print(line)
    fnull.close()


def __get_number_of_certain_stats_line(opt_flags, program, line_a, line_b=None,
                                       amount=False):
    """Returns the number of the specified line in the statistic retrieved from
    the opt call if the argument line_b is not specified and the difference of
    the number of the line_b and the number of line_a if line_b is specified.

    Args:
        opt_flags (list[string]): a list containing the flags for the opt call
        program (string): the name of the application Polly should detect
            SCoPs in.
        line_a (string): the string representation of the first line that
            should be grabbed.
        line_b (string, optional): the string representation of the second
            line that should be grabbed.
        amount (boolean): should the amount be calculated.

    Returns:
        int: the difference between the line_a and line_b or just the
        corresponding number of line_a if line_b is None.
    """
    command = []
    command.extend(OPT_CALL)
    command.extend(opt_flags)
    command.extend(STATS_FLAGS)
    command.append(program)
    fnull = open(os.devnull, 'w')
    p = compiler(CFG["compiler"]["cxx"].value())
    _, stderr = p.communicate()
    stderr = stderr.splitlines()

    # Catch the result and return the number of detected SCoPs
    a = 0
    b = float('inf')

    for line in stderr:
        line = (str(line))

        if line_a in line:
            number = ''
            for i in range(len(line)):
                if '0' <= line[i] <= '9':
                    number += line[i]
            try:
                a = int(number)
            except ValueError:
                line_b = None
                a = float('inf')
                break
        elif line_b is not None and line_b in line:
            number = ''
            for i in range(len(line)):
                if '0' <= line[i] <= '9':
                    number += line[i]
            try:
                b = int(number)
            except ValueError:
                line_b = None
                a = float('inf')
                break
    fnull.close()

    if line_b is None:
        result = a
    else:
        if amount:
            result = (b - a) / b
        else:
            result = max(b - a, 0)

    return result


def get_number_of_scops(opt_flags, program):
    """Returns the number of SCoPs Polly can detect in the provided program.

    Args:
        opt_flags (list[string]): a list containing the flags for the opt call.
        program (string): the name of the application Polly should detect
            SCoPs in.

    Returns:
        int: the number of detected SCoPs.
    """
    return __get_number_of_certain_stats_line(opt_flags, program, ('Number '
                                                                   'of '
                                                                   'weighted '
                                                                   'regions '
                                                                   'that a '
                                                                   'valid '
                                                                   'part of '
                                                                   'Scop'))


def get_number_of_weighted_scops(opt_flags, program):
    """Returns the weighted number of SCoPs Polly can detect in the provided
    program.

    Args:
        opt_flags (list[string]): a list containing the flags for the opt call.
        program (string): the name of the application Polly should detect
            SCoPs in.

    Returns:
        int: the weighted number of detected SCoPs.
    """
    return __get_number_of_certain_stats_line(opt_flags, program, ('Weighted '
                                                                   'number '
                                                                   'of regions'
                                                                   ' that are '
                                                                   'a valid '
                                                                   'Scop'))


def get_number_of_regions(opt_flags, program):
    """Returns the number of regions in the provided program.

    Args:
        opt_flags (list[string]): a list containing the flags for the opt call.
        program (string): the name of the application Polly should detect
            regions in.

    Returns:
        int: the number of regions.
    """
    return __get_number_of_certain_stats_line(opt_flags, program, 'The # of '
                                                                  'regions')


def get_regions_without_scops(opt_flags, program):
    """Returns the difference between the number of regions and the number of
    SCoPs.

    Args:
        opt_flags (list[string]): a list containing the flags for the opt call
        program (string): the name of the application Polly should detect
            SCoPs in.

    Returns:
        int: the difference between the number of regions and the number of
        detected SCoPs.
    """
    return __get_number_of_certain_stats_line(opt_flags, program,
                                              ('Weighted number of regions '
                                               'that are a valid Scop'),
                                              'The # of regions')


def get_amount_of_bad_regions(opt_flags, program):
    return __get_number_of_certain_stats_line(opt_flags, program,
                                              ('Weighted number of regions '
                                               'that are a valid Scop'),
                                              'The # of regions', True)
