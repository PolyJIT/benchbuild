#!/usr/bin/env python
"""This module supplies a function that can generate custom sequences of
optimization passes for arbitrary programs.

This module provides an implementation of a hill climber algorithm presented by
Kulkarni in his paper "Evaluating Heuristic Optimization Phase Order Search
Algorithms" (published 2007). The algorithm is used to generate a custom
optimization sequence for an arbitrary application. The resulting sequence
is a list of flags that can be set by the LLVM opt tool. The generated
sequence is meant to be a good flag combination that increases the amount of
code that can be detected by Polly.
"""
import random
import multiprocessing
import logging

import benchbuild.experiments.sequences.polly_stats as polly_stats


__author__ = "Christoph Woller"
__credits__ = ["Christoph Woller"]
__maintainer__ = "Christoph Woller"
__email__ = "wollerch@fim.uni-passau.de"

# Default values
DEFAULT_PASS_SPACE = ['-basicaa', '-mem2reg']
DEFAULT_SEQ_LENGTH = 10
DEFAULT_ITERATIONS = 100

print_debug = False


def create_random_sequence(pass_space, seq_length):
    """Creates a random sequence.

    This methods generates a sequence by randomly picking available passes.

    Args:
        pass_space (list[string]): contains the available passes.
        seq_length (int): the length the sequence should have.
    Returns:
        list: the created sequence.
     """
    sequence = []

    for _ in range(seq_length):
        sequence.append(random.choice(pass_space))

    return sequence


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


def calculate_neighbours(sequence, seq_to_fitness, pass_space, program):
    """Calculates the neighbours of the specified sequence.

    This method calculates all sequences that differ from the specified
    sequence at exactly one position. Furthermore this method calculates the
    fitness values of the neighbours.
    A sequence is a neighbour of another sequence if they have exactly one
    different pass.

    E.g.: Sequences s1 = [a, a], s2 = [a, b], s3 = [b, b].
    s2 is a neighbour of s1, because they differ in the second position.
    s3 is not a neighbour of s1, because they differ in position one and
    two.

    Args:
        sequence (list[string]): the specified sequence.
        seq_to_fitness (dict): dictionary that contains calculated fitness
            values.
        pass_space (list[string]): a list of all available passes.
        program (string): the name of the application the neighbour
            sequences should be used for.

    Returns:
        list[list[string]]: all neighbours of the specified sequence are
            returned as list.
    """
    neighbours = []
    pool = multiprocessing.Pool()
    pool.apply_async(calculate_fitness_value,
                     args=(sequence, seq_to_fitness, str(sequence), program))

    for i in range(len(sequence)):
        remaining_passes = list(pass_space)
        remaining_passes.remove(sequence[i])

        # Create sequences with different pass at position i.
        for remaining_pass in remaining_passes:
            neighbour = list(sequence)
            neighbour[i] = remaining_pass
            pool.apply_async(calculate_fitness_value,
                             args=(neighbour, seq_to_fitness, str(neighbour),
                                   program))
            neighbours.append(neighbour)

    pool.close()
    pool.join()

    return neighbours


def climb(sequence, program, pass_space, seq_to_fitness):
    """Performs the actual hill climbing.

    Args:
        sequence (list[string]): the sequence that should be used as base
            sequence.
        program (string): name of the application the sequences are applied
            on.
        pass_space (list[string]): a list containing all available passes.
        seq_to_fitness (dict): dictionary that stores calculated fitness
            values.
    """
    log = logging.getLogger(__name__)
    base_sequence = sequence
    base_sequence_key = str(base_sequence)
    log.debug("Start climbing...")
    log.debug("Initial base sequence: %s", str(base_sequence))

    # Take the base sequence and calculate all neighbours. Check if the best
    # performing neighbour is better than the base sequence. If this is the
    # case this neighbour becomes the new base sequence.
    # This process is repeated until the base sequence outperforms all its
    # neighbours.
    climbs = 0
    changed = True

    while changed:
        changed = False

        # Calculate its neighbours.
        neighbours = calculate_neighbours(base_sequence, seq_to_fitness,
                                          pass_space, program)

        # Check if there is a better performing neighbour.
        for neighbour in neighbours:
            if seq_to_fitness[base_sequence_key] \
                    > seq_to_fitness[str(neighbour)]:
                base_sequence = neighbour
                base_sequence_key = str(neighbour)
                changed = True

        climbs += 1
        log.debug("\n---> Climb number %s <---", str(climbs))
        log.debug("---> Base sequence: %s <---", str(base_sequence))
        log.debug("---> Neighbours: <---")

        if print_debug:
            for neighbour in neighbours:
                log.debug('Neighbour: %s; Fitness value: %s',
                          str(neighbour),
                          str(seq_to_fitness[str(neighbour)]))


    log.debug("Local optimum reached!\n")
    return base_sequence


def generate_custom_sequence(program, pass_space=DEFAULT_PASS_SPACE,
                             seq_length=DEFAULT_SEQ_LENGTH,
                             iterations=DEFAULT_ITERATIONS, debug=False):
    """Generates a custom optimization sequence for a provided application.

    Args:
        program (string): the name of the application a custom sequence should
            be generated for.
        pass_space (list[string], optional): list of passes that should be
            taken into consideration for the generation of the custom
            sequence.
        seq_length(int, optional): the length of the sequence that should be
            generated.
        iterations (int, optional): the number of times the hill climbing
            process is to be repeated.
        debug (boolean, optional): true if debug information should be printed;
            false otherwise.

    Returns:
        list[string]: the generated custom optimization sequence. Each element
            of the list represents one optimization pass.
    """
    global print_debug
    print_debug = debug
    log = logging.getLogger(__name__)

    best_sequence = []
    seq_to_fitness = multiprocessing.Manager().dict()
    log.debug("\n Start hill climbing algorithm...")

    for i in range(iterations):
        log.debug("Iteration: %d", i + 1)
        base_sequence = create_random_sequence(pass_space, seq_length)
        base_sequence = climb(base_sequence, program, pass_space,
                              seq_to_fitness)

        if not best_sequence or seq_to_fitness[str(best_sequence)] < \
                seq_to_fitness[str(base_sequence)]:
            best_sequence = base_sequence

    log.debug("Best sequence found in %d iterations:")
    log.debug("Sequence: %s", best_sequence)
    log.debug("Fitness value: %s", str(seq_to_fitness[str(best_sequence)]))

    return best_sequence
