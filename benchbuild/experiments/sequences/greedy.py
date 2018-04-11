#!/usr/bin/env python
"""This module supplies a function that can generate custom sequences of
optimization passes for arbitrary programs.

This module provides an implementation of a greedy algorithm presented by
Kulkarni in his paper "Evaluating Heuristic Optimization Phase Order Search
Algorithms" (published 2007). The algorithm is used to generate a custom
optimization sequence for an arbitrary application. The resulting sequence
is a list of flags that can be set by the LLVM opt tool. The generated
sequence is meant to be a good flag combination that increases the amount of
code that can be detected by Polly.
"""
import random
import operator
import multiprocessing
import logging

import benchbuild.experiments.sequences.polly_stats as polly_stats


__author__ = "Christoph Woller"
__credits__ = ["Christoph Woller"]
__maintainer__ = "Christoph Woller"
__email__ = "wollerch@fim.uni-passau.de"

# DEFAULT VALUES
DEFAULT_PASS_SPACE = ['-basicaa', '-mem2reg']
DEFAULT_SEQ_LENGTH = 10
DEFAULT_DEBUG = False
DEFAULT_NUM_ITERATIONS = 100


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


def generate_custom_sequence(program, pass_space=DEFAULT_PASS_SPACE,
                             seq_length=DEFAULT_SEQ_LENGTH,
                             iterations=DEFAULT_NUM_ITERATIONS,
                             debug=DEFAULT_DEBUG):
    """Generates a custom optimization sequence for a provided application.

    This method generates a custom optimization sequence with the help of a
    greedy algorithm. The algorithm views the search space as DAG with the
    empty sequence as root node. The root node has n children. One child for
    each available pass. The nodes representing sequences with length 1 have a
    total number of 2n children. n children represent the effect of
    prepending each of the available n passes and n children represent
    the effect of appending the available n passes.
    The algorithm starts at the root node and walks along to the child with
    the highest fitness value. This process is repeated till we get to a
    node representing a sequence with the desired length. If there are
    children with equal fitness values a random node will be picked.

    Args:
        program (string): the name of the application a custom sequence should
            be generated for.
        pass_space (list[string], optional): list of passes that should be
            taken into consideration for the generation of the custom
            sequence.
        seq_length (int, optional): the length of the sequence that should be
            generated.
        iterations (int, optional): the number of iterations the algorithm
            should be repeated in order to reduce the noise.
        debug (boolean, optional): true if debug information should be
            printed; false otherwise.

    Returns:
        list[string]: the generated custom optimization sequence. Each element
            of the list represents one optimization pass.
    """
    generated_sequences = []
    seq_to_fitness = multiprocessing.Manager().dict()

    log = logging.getLogger(__name__)
    for i in range(iterations):
        log.debug("=======================================")
        log.debug("Iteration: %d", i + 1)
        log.debug("=======================================")
        base_sequence = []

        log.debug("Start Greedy Algorithm with empty sequence as root...")

        while len(base_sequence) < seq_length:
            log.debug(
                "<=--------------------------------------------------------=>")
            log.debug("Custom Sequence: %s", str(base_sequence))
            log.debug("Length: %d", len(base_sequence))
            log.debug("---------------------------------")
            log.debug("Child Sequences: ")

            sequences = []
            pool = multiprocessing.Pool()

            for flag in pass_space:
                # Create new sequence by appending a new flag.
                seq_append = list(base_sequence) + [flag]

                pool.apply_async(calculate_fitness_value, args=(
                    seq_append, seq_to_fitness, str(seq_append), program))
                sequences.append(seq_append)
                log.debug(str(seq_append))

                if base_sequence:
                    # Create new sequence by depending a new flag.
                    seq_prepend = [flag] + list(base_sequence)
                    pool.apply_async(calculate_fitness_value, args=(
                        seq_prepend, seq_to_fitness, str(seq_prepend),
                        program))
                    sequences.append(seq_prepend)
                    log.debug(str(seq_prepend))

            pool.close()
            pool.join()

            # Sort the sequences by its fitness value and reverse the list
            # because the sequence with the lowest fitness value is the best.
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
                    sequences.insert(0, other)
                    equal = False

            base_sequence = random.choice(fittest_sequences)

            log.debug(
                "<=--------------------------------------------------------=>")

        generated_sequences.append(base_sequence)

    generated_sequences.sort(key=lambda s: seq_to_fitness[str(s)])
    log.debug("\n...Finished!")
    log.debug(
        "Generated Custom Sequences in %s Iterations:", str(iterations))
    if debug:
        for generated in generated_sequences:
            log.debug(generated)

    if debug:
        sorted_seq = sorted(seq_to_fitness.iteritems(),
                            key=operator.itemgetter(1))
        log.debug('\nBest sequences found over iterations:')
        for i in range(min(len(sorted_seq), 10)):
            log.debug(sorted_seq.pop())

        log.debug("\n")

    best_sequence = generated_sequences.pop()
    log.debug("\nBest Custom Sequence: ")
    log.debug(str(best_sequence))

    return best_sequence
