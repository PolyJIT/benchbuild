# !/usr/bin/env python
"""This module supplies functionality to create different statistics of the
results of the heuristic algorithms.
"""
import csv
import getopt
import sys
import logging

import pprof_utilities


__author__ = "Christoph Woller"
__credits__ = ["Christoph Woller"]
__maintainer__ = "Christoph Woller"
__email__ = "wollerch@fim.uni-passau.de"

# Default file information.
DEFAULT_FILE_PATH = '<filepath>'

# csv file that contains fitness information for the different sample programs
# for each tested sequence.
FITNESS_CSV = 'fitness_comparison.csv'
BEST_SEQUENCES_RAW = 'raw.best-sequences.raw'
FLAG_CSV = 'flags-stats.csv'

# File name of the file that contains the sequences the should be considered
#  for the calculation of the most frequent optimization flags.
FLAG_STATS_RAW = 'raw.heuristic-compilestats.raw'
DEFAULT_STATS = '.heuristic-compilestats.raw'

# Information about preformed experiments.
CUSTOM = {'genetic 1 length 10': 10, 'genetic 1 length 20': 20,
          'genetic 2 length 10': 10, 'genetic 2 length 20': 20}
FIXED = ['O3 & polly-canonicalize', 'polly-canonicalize', 'empty sequence']


def __calculate_best_sequences(file_path, file):
    """Checks for each program which custom sequence has the highest fitness
     value.

     Args:
        file (string): the name of the csv file that contains the fitness value
            of the different sequences for each program.
        file_path (string): the path to the file.
    Returns
        dict: dictionary that contains for each program the best custom
            sequence.
     """
    # Read in csv file and parse information.
    reader = csv.reader(open(file_path + file, 'r'))
    program_to_experiment = {}
    experiments = []
    first = True

    for row in reader:
        if first:
            for i in range(1, len(row)):
                experiments.append(row[i])
                first = False
        else:
            program = row[0]
            experiment_to_fitness = {}

            for i in range(1, len(row)):
                experiment_to_fitness[experiments[i - 1]] = row[i]

            program_to_experiment[program] = experiment_to_fitness

    program_to_custom = {}

    for prog in program_to_experiment:
        experiment_to_fitness = program_to_experiment[prog]

        max_value = float('inf')

        # Get best value of the fixed sequences
        for exp in FIXED:
            fitness = float(experiment_to_fitness[exp])
            if fitness < max_value:
                max_value = fitness

        for exp in CUSTOM:
            fitness = float(experiment_to_fitness[exp])
            if fitness <= max_value:
                if prog in program_to_custom:
                    l = program_to_custom[prog]
                    fitness_old = float(experiment_to_fitness[l[0]])

                    if fitness < fitness_old:
                        l = [exp]
                    elif fitness == fitness_old:
                        if CUSTOM[l[0]] == CUSTOM[exp]:
                            l.append(exp)
                        elif CUSTOM[l[0]] > CUSTOM[exp]:
                            l = [exp]

                    program_to_custom[prog] = l
                else:
                    program_to_custom[prog] = [exp]

    return program_to_custom


def __create_flag_statistics_csv(file_path, file_name, csv_name=FLAG_CSV):
    """Creates csv file that lists the occurrences of flags in the sequences
    found in the specified file.
    """
    total_flag_occurrence = {}
    flag_occurrence_seq = {}
    flag_count = 0
    sequences = pprof_utilities.read_sequences(file_path, file_name)

    for sequence in sequences:
        flag_occurred = {}
        for flag in sequence:
            flag_count += 1
            total_flag_occurrence[
                flag] = 1 if flag not in total_flag_occurrence \
                else total_flag_occurrence[flag] + 1

            if flag not in flag_occurred:
                flag_occurred[flag] = True
                flag_occurrence_seq[
                    flag] = 1 if flag not in flag_occurrence_seq \
                    else flag_occurrence_seq[flag] + 1

    # Write the gathered information in a new csv file.
    with open(file_path + csv_name, 'w', newline='') as csvfile:
        w = csv.writer(csvfile, delimiter=' ')
        w.writerow(['Flag', 'Sequences', 'Total', 'TotalNumberSequences',
                    'TotalNumberFlags'])

        for flag in total_flag_occurrence:
            w.writerow([str(flag), str(flag_occurrence_seq[flag]),
                        str(total_flag_occurrence[flag]), str(len(sequences)),
                        str(flag_count)])


def __create_best_sequences_raw(file_path, file_name, dest_name, stats_suffix):
    """Create a raw file that contains the best sequences for each program."""
    program_to_custom = __calculate_best_sequences(file_path, file_name)
    output = open(file_path + dest_name, 'w', newline='')

    for program in program_to_custom:
        output.write('--------------------\n')
        output.write('Program: ' + program + '\n')

        for exp in program_to_custom[program]:
            output.write('Experiment: ' + exp + '\n')
            stats = exp + '/' + program + stats_suffix
            sequence = pprof_utilities.read_sequence(file_path, stats)
            output.write('Optimization Passes: ' + str(sequence) + '\n')

        output.write('\n')


def create_best_sequences_stats():
    """Create the report file for the best sequences found. A csv file
    containing the fitness values of the different sequences is required for
    this calculations. The R script plot_fitness_value.R provides
    functionality to create such a csv file from a heuristic-compilestats
    csv file."""
    __create_best_sequences_raw(DEFAULT_FILE_PATH, FITNESS_CSV,
                                BEST_SEQUENCES_RAW, DEFAULT_STATS)


def create_flag_stats():
    __create_flag_statistics_csv(DEFAULT_FILE_PATH, FLAG_STATS_RAW)


def __find_frequent_subsequences(sequences):
    """Tries to find frequent subsequences in the specified list of sequences.
    """
    passes = set()

    for sequence in sequences:
        for p in sequence:
            passes.add(p)

    passes = list(passes)

    subsequences = []
    for p in passes:
        subsequences.append([p])
    occurrences = {}

    while subsequences:
        new_subsequences = []

        for subsequence in subsequences:
            for p in passes:
                new_subsequence = list(subsequence)
                new_subsequence.append(p)
                new_subsequences.append(new_subsequence)

        subsequences = new_subsequences

        for subsequence in subsequences:
            for sequence in sequences:
                contained = True

                for i in range(len(subsequence)):
                    if len(sequence) >= len(subsequence[i::]) \
                            and subsequence[i] in sequence:
                        index = sequence.index(subsequence[i])
                        sequence = sequence[(index + 1)::]
                    else:
                        contained = False
                        break

                if contained:
                    if str(subsequence) in occurrences:
                        occurrences[str(subsequence)] += 1
                    else:
                        occurrences[str(subsequence)] = 1

        remaining = []
        for subsequence in subsequences:
            key = str(subsequence)
            if key in occurrences and occurrences[key] >= 2:
                remaining.append(subsequence)

        subsequences = remaining

    return occurrences


def find_patterns_in_sequences(file_path, file_name):
    """Searches for frequently occurring subsequences in the sequences listed
    in the specified file. The results are written to a new file in the
    specified path.
    """
    sequences = pprof_utilities.read_sequences(file_path, file_name)
    occurrences = __find_frequent_subsequences(sequences)
    keys = [k for k, v in occurrences.items() if v >= 2]
    total_num_sequences = len(sequences)
    frequent_occurrences = dict()

    for pattern in keys:
        if occurrences[pattern] / total_num_sequences >= 0.2:
            frequent_occurrences[pattern] = occurrences[pattern]

    with open(file_path + 'subsequence_occurrences.csv',
              'w', newline='') as \
            file:
        w = csv.writer(file, delimiter=' ')
        w.writerow(['Subsequence', 'Occurrences', 'TotalNumberSequences'])

        for pattern in keys:
            w.writerow([str(pattern), str(occurrences[pattern]),
                        str(total_num_sequences)])


def __usage():
    """Prints out the usage of this python script."""
    logging.getLogger(__name__).warning('Wrong usage!\n'
          + 'You have to provide one of the following flags:\n'
          + '--best-sequences: searches for the best custom sequences and '
            'generates an overview raw and csv file.'
          + '--subsequences: searches for frequently occurring subsequences '
            'in the sequences found in the specified file.'
          + '-h / --help: prints the help text.')


def main(argv):
    """Starts the generation of the custom compilation sequence."""
    try:
        opts, args = getopt.getopt(argv, 'h', ['help', 'best-sequences',
                                               'subsequences', 'flagstats'])
    except getopt.GetoptError:
        create_best_sequences_stats()
        sys.exit(2)
    for opt, _ in opts:
        if opt in ('-h', '--help'):
            __usage()
            sys.exit()
        elif opt == '--best-sequences':
            create_best_sequences_stats()
        elif opt == '--flagstats':
            create_flag_stats()
        elif opt == '--subsequences':
            if args:
                find_patterns_in_sequences(DEFAULT_FILE_PATH, args[0])
            else:
                __usage()


if __name__ == '__main__':
    main(sys.argv[1:])
