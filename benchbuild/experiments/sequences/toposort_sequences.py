#!/usr/bin/env python
"""This module provides functionality to create a custom preoptimization
sequence from a directed acyclic graph (DAG) using topological sorting.

In the current version the DAG have to be specified manually via constants.
"""
import multiprocessing
import random
import logging

import topsort
import benchbuild.experiments.sequences.polly_stats as polly_stats


__author__ = "Christoph Woller"
__credits__ = ["Christoph Woller"]
__maintainer__ = "Christoph Woller"
__email__ = "wollerch@fim.uni-passau.de"


# Directed edges of the dependency graph.
# The dependencies have to specified manually.
NUM_TO_PASS = {
    1: '-mem2reg', 2: '-early-cse', 3: '-inline', 4: '-sroa', 5: '-globalopt',
    6: '-functionattrs', 7: '-instcombine', 8: '-gvn', 9: '-ipsccp',
    10: '-basicaa', 11: '-jump-threading', 12: '-simplifycfg',
    13: '-polly-indvars', 14: '-loop-unroll', 15: '-globaldce',
    16: '-polly-prepare'
}
PASS_TO_NUM = {v: k for k, v in NUM_TO_PASS.items()}
DEPENDENCIES = [
    (1, 2), (1, 3),
    (3, 4), (3, 5), (3, 6),
    (6, 7),
    (7, 8),
    (8, 9),
    (9, 10),
    (10, 11), (10, 12),
    (11, 13), (12, 13),
    (13, 14), (13, 15), (13, 16)
]


def __create_sequences():
    """Creates optimization sequences using a dependency graph and
    topological sort.
    """
    number_of_nodes = len(PASS_TO_NUM)

    # Use Varol's and Rotem's topological sorting algorithm to get all
    # topological sorting arrangements.
    grid = topsort.partial_order_to_grid(DEPENDENCIES, number_of_nodes)
    sortings = topsort.vr_topsort(number_of_nodes, grid)

    sequences = []
    for sort in sortings:
        sequence = [NUM_TO_PASS[num] for num in sort]
        sequences.append(sequence)

    return sequences


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


def generate_custom_sequence(program):
    """"Generates optimization sequences from a dependency graph and calculates
    the best of these sequences for the specified program."""
    log = logging.getLogger(__name__)
    # Get different topological sorting arrangements.
    sequences = __create_sequences()
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

    log.debug("Best sequences %d", len(fittest_sequences))
    for sequence in fittest_sequences:
        log.debug("Best: %s", str(sequence))
    log.debug("---------------------------------------------------------------")

    return random.choice(fittest_sequences)
