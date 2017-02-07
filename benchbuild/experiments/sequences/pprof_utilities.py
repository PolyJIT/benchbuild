#!/usr/bin/env python
"""This module supplies utility functions."""
import shutil

__author__ = "Christoph Woller"
__credits__ = ["Christoph Woller"]
__maintainer__ = "Christoph Woller"
__email__ = "wollerch@fim.uni-passau.de"


START_OPT_SEQUENCE = 'Optimization Passes'



def copy_file_to(src_path, src_name, dest_path, dest_name):
    """Helper function to copy a file."""
    input_file = src_path + src_name
    output_file = dest_path + dest_name

    shutil.copyfile(input_file, output_file)


def parse_line_to_sequence(line, prefix=START_OPT_SEQUENCE):
    """Transforms a line of a raw file into a sequence."""
    if prefix in line:
        rest = line.split('[')[1]
        rest = rest[:len(rest) - 2]
        rest = rest.replace(' ', '')
        rest = rest.replace("'", '')
        return rest.split(',')

    return []


def read_sequence(file_path, file_name, prefix=START_OPT_SEQUENCE):
    """Read in a sequence from a certain raw file."""
    try:
        file = open(file_path + file_name, 'r')
    except IOError:
        return []

    sequence = []

    for line in file:
        if prefix in line:

            sequence = parse_line_to_sequence(line)
            break

    file.close()
    return sequence


def read_sequences(file_path, file_name, prefix=START_OPT_SEQUENCE):
    """Read in all sequences that are listed in the specified file."""
    try:
        file = open(file_path + file_name)
    except IOError:
        return []

    sequences = []

    # Check for the custom optimization sequences in the raw file.
    for line in file:
        if prefix in line:
            sequence = parse_line_to_sequence(line, prefix)
            if sequence:
                sequences.append(sequence)

    file.close()
    return sequences
