#!/usr/bin/env python
"""This module provides functionality to examine heuristic-compilestats raw
files of to check which sequences appear most frequently.
"""
import os
import logging

import pprof_utilities


__author__ = "Christoph Woller"
__credits__ = ["Christoph Woller"]
__maintainer__ = "Christoph Woller"
__email__ = "wollerch@fim.uni-passau.de"

# Where is the reports file located?
FILE_PATH = '<location of reports>'

# What is the prefix for an optimization sequence in this file?
PREFIX = 'Optimization Passes'


def find_most_frequent_sequence():
    """Search the heuristic-compilestats files for frequently occurring
    best sequences.
    """
    log = logging.getLogger(__name__)
    sequence_to_programs = dict()
    number_programs = 0

    for file in os.listdir(FILE_PATH):
        if not file.startswith('raw.') and file.endswith(
                '.heuristic-compilestats.raw'):
            sequences = pprof_utilities.read_sequences(FILE_PATH, str(file),
                                                       prefix=PREFIX)
            if sequences:
                number_programs += 1
            for sequence in sequences:
                sequence_tuple = tuple(sequence)
                if sequence_tuple in sequence_to_programs:
                    sequence_to_programs[sequence_tuple] += 1
                else:
                    sequence_to_programs[sequence_tuple] = 1

    sequences = sorted(sequence_to_programs,
                       key=lambda key: sequence_to_programs[key])
    best = sequences.pop()
    best_sequences = [best]
    frequency = sequence_to_programs[best]

    for sequence in sequences:
        if sequence_to_programs[sequence] == frequency:
            best_sequences.append(sequence)

    log.info("Number of best sequences: %s", str(len(best_sequences)))
    log.info("Most frequently occurring sequence:")
    log.info(best)
    log.info("Occurrences: %s of %d",
             str(sequence_to_programs[best]),
             str(number_programs))

    for sequence in best_sequences:
        log.info("Best: %s", str(list(sequence)))


if __name__ == '__main__':
    find_most_frequent_sequence()
