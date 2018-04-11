#!/usr/bin/env python
"""
This module supplies functionality to shorten the custom optimization
sequence for an arbitrary program found by an arbitrary heuristic approach.
"""
import sys
import getopt
import multiprocessing
import logging

import benchbuild.experiments.sequences.polly_stats as polly_stats
import pprof_utilities


__author__ = "Christoph Woller"
__credits__ = ["Christoph Woller"]
__maintainer__ = "Christoph Woller"
__email__ = "wollerch@fim.uni-passau.de"


DEFAULT_FILE_PATH = '<filepath>'

debug = False


# --- Helper Functions ---
def calculate_fitness(sequence, seq_to_fitness, key, program):
    """Calculates the fitness value of this sequence."""
    seq_to_fitness[key] = polly_stats.get_regions_without_scops(sequence,
                                                                program)


def prepare_sequence(sequence_string):
    """Takes a sequence as string and converts it into a list containing the
    passes of the sequence.
    """
    result = sequence_string.replace('[', '')
    result = result.replace(']', '')
    result = result.replace(' ', '')
    result = result.replace("'", '')

    if len(result):
        return result.split(',')
    else:
        return []


# --- Optimization Functions ---
def shorten_sequence(base_sequence, seq_to_fitness, program):
    """Tries to shorten this sequence by omitting flag by flag and checking if
        the smaller sequence has at least the same fitness value as the
        original one.
    """
    key_base_sequence = str(base_sequence)
    sequences = set()
    current_sequences = set()

    # Create all sequences that contain one flag less than the base sequence.
    for i in range(len(base_sequence)):
        seq = list(base_sequence)
        seq.pop(i)
        current_sequences.add(tuple(seq))

    # Shorten the sequences until there are no more changes.
    while current_sequences:
        # Calculate the fitness of the sequences.
        pool = multiprocessing.Pool()

        for seq in current_sequences:
            sequence = list(seq)
            pool.apply_async(calculate_fitness, args=(
                sequence, seq_to_fitness, str(sequence), program))

        pool.close()
        pool.join()

        # Check if the smaller sequences are better or equal as the original
        # sequence. If this is true, mark the smaller sequence for shortening.
        to_shorten = set()

        for seq in current_sequences:
            if seq_to_fitness[str(list(seq))] \
                    <= seq_to_fitness[key_base_sequence]:
                to_shorten.add(seq)

        sequences = sequences.union(current_sequences)

        # Create smaller sequences for next round
        current_sequences = set()

        while to_shorten:
            seq = to_shorten.pop()

            for i in range(len(seq)):
                new_seq = list(seq)
                new_seq.pop(i)
                current_sequences.add(tuple(new_seq))


def shorten_sequence_recursively(base_sequence, seq_to_fitness, program):
    """Tries to shorten this sequence by omitting flag by flag and checking if
        the smaller sequence has at least the same fitness value as the
        original one. This method is the recursive approach of the method
        "shorten_sequence".
    """
    sequences = []
    pool = multiprocessing.Pool()

    # Calculate all sequences that contain a flag less.
    for i in range(len(base_sequence)):
        smaller_sequence = list(base_sequence)
        smaller_sequence.pop(i)

        if str(smaller_sequence) not in seq_to_fitness:
            sequences.append(smaller_sequence)
            pool.apply_async(calculate_fitness, args=(
                smaller_sequence, seq_to_fitness, str(smaller_sequence),
                program))

    pool.close()
    pool.join()

    # Check if the smaller sequences are better or equal as the original
    # sequence. If this is true, try to shorten the smaller sequence.
    for seq in list(sequences):
        if seq_to_fitness[str(seq)] <= seq_to_fitness[str(base_sequence)]:
            shorten_sequence_recursively(seq, seq_to_fitness, program)


def build_shorter_sequence(base_sequence, seq_to_fitness, program):
    """Tries to build a sequence that is shorter than the base sequence but
    has at least the same fitness value as the base sequence.
    """
    clusters = set()
    current_clusters = set()
    indexes = list(range(len(base_sequence)))
    finished = False
    calculate_fitness(base_sequence, seq_to_fitness, str(indexes), program)

    for i in indexes:
        current_clusters.add(frozenset([i]))

    while not finished:
        pool = multiprocessing.Pool()

        for cluster in current_clusters:
            seq = list(base_sequence[i] for i in cluster)
            pool.apply_async(calculate_fitness, args=(
                seq, seq_to_fitness, str(sorted(cluster)), program))

        pool.close()
        pool.join()

        # Check if the smaller sequences are better or equal as the original
        # sequence. If this is true, try to shorten the smaller sequence.
        for cluster in current_clusters:
            if seq_to_fitness[str(sorted(cluster))] <= \
                    seq_to_fitness[str(indexes)]:
                finished = True

        clusters = clusters.union(current_clusters)
        new_clusters = set()

        while current_clusters and not finished:
            cluster = current_clusters.pop()

            for other in current_clusters:
                new_cluster = cluster.union(other)

                if new_cluster not in clusters:
                    new_clusters.add(new_cluster)

        current_clusters = new_clusters


def start_shortening(experiment, program):
    """ Reads the raw output file of the specified program generated by the
    specified experiment and tries to shorten the custom optimization
    sequence.

    Args:
        experiment (string): the name of the experiment that generated the
            raw file of the specified program.
        program (string): the name of the application from which the custom
            optimization sequence should be shortened.
    """
    log = logging.getLogger(__name__)
    file_name = experiment + '/' + program + '.heuristic-compilestats.raw'
    sequence = pprof_utilities.read_sequence(DEFAULT_FILE_PATH, file_name)
    seq_to_fitness = multiprocessing.Manager().dict()

    if sequence:
        program += '.bc'
        calculate_fitness(sequence, seq_to_fitness, str(sequence), program)
        shorten_sequence(sequence, seq_to_fitness, program)

        best_sequences = [k for k, x in seq_to_fitness.items() if
                          not any(y < x for y in seq_to_fitness.values())]
        best = prepare_sequence(best_sequences.pop())

        for s in best_sequences:
            seq = prepare_sequence(s)

            if len(seq) < len(best):
                best = seq

        log.debug("Optimization Passes: %s", str(best))
        polly_stats.detect_scops(best, program)
    else:
        log.error('Error! Could not find sequence in raw file!')


def __usage():
    """Prints out the usage of this python script."""
    logging.getLogger(__name__).warning('Wrong usage!\n'
          'Usage: optimize_sequence --experiment=exp --program=prog')


def main(argv):
    """Starts the shortening of the custom compilation sequence."""
    global debug
    experiment = None
    program = None

    try:
        opts, args = getopt.getopt(argv, 'hep:',
                                   ['help', 'experiment=', 'program='])

    except getopt.GetoptError:
        __usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            __usage()
            sys.exit()
        elif opt in ('-e', '--experiment'):
            experiment = arg
        elif opt in ('-p', '--program'):
            program = arg
        else:
            __usage()
            sys.exit()

    if experiment and program:
        debug = False
        start_shortening(experiment, program)
    else:
        __usage()


if __name__ == '__main__':
    main(sys.argv[1:])
