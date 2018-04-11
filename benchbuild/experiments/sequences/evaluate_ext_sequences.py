#!/usr/bin/env python
"""This module provides functionality to create a custom preoptimization
sequence from a directed acyclic graph (DAG) using topological sorting.

In the current version the DAG have to be specified manually via constants.
"""
import multiprocessing
import random
import logging

import benchbuild.experiments.sequences.polly_stats as polly_stats
import pprof_utilities

__author__ = "Christoph Woller"
__credits__ = ["Christoph Woller"]
__maintainer__ = "Christoph Woller"
__email__ = "wollerch@fim.uni-passau.de"


SEQUENCE_FILE_PATH = '.../pprof-study/results/'
SEQUENCE_FILE = 'best_sequences.raw'
SEQUENCE_PREFIX = 'Best: '


def calculate_fitness_value(sequence, seq_to_fitness, key, program):
    """Calculates the fitness value of the provided sequence.

    This method calculates the fitness of the sequence by using the number
    of regions that are no valid SCoPs if this sequence is used for
    preoptimization before Polly's SCoP detection.

    Args:
        sequence (list[string]): the sequence for that the fitness value should
            be calculated.
        seq_to_fitness (dict): dictionary that stores calculated fitness
            values.
        key (string): the key of the provided sequence for the dictionary.
        program (string): the name of the application this sequence
            should be used for.
    """
    if key not in seq_to_fitness:
        seq_to_fitness[key] = polly_stats.get_regions_without_scops(sequence,
                                                                    program)


def evaluate_best_sequence(program):
    """"Generates optimization sequences from a dependency graph and calculates
    the best of these sequences for the specified program."""
    log = logging.getLogger(__name__)
    # Get different topological sorting arrangements.
    sequences = pprof_utilities.read_sequences(SEQUENCE_FILE_PATH,
                                               SEQUENCE_FILE, SEQUENCE_PREFIX)
    possible_sequences = len(sequences)
    seq_to_fitness = multiprocessing.Manager().dict()
    pool = multiprocessing.Pool()

    # Calculate the fitness value of the topological sorting arrangements.
    for sequence in sequences:
        pool.apply_async(calculate_fitness_value, args=(
            sequence, seq_to_fitness, str(sequence), program))

    pool.close()
    pool.join()

    # Get the best sequences.
    sequences.sort(key=lambda s: seq_to_fitness[str(s)])
    sequences = sequences[::-1]
    fittest = sequences.pop()
    fittest_fitness_value = seq_to_fitness[str(fittest)]
    fittest_sequences = [fittest]
    equal = True

    while sequences and equal:
        other = sequences.pop()
        if seq_to_fitness[str(other)] == fittest_fitness_value:
            fittest_sequences.append(other)
        else:
            equal = False

    log.info("Best sequences %d of %s", len(fittest_sequences),
             str(possible_sequences))
    for sequence in fittest_sequences:
        log.info("Best: %s", str(sequence))
    log.info("----------------------------------------------------------------")

    return random.choice(fittest_sequences)
