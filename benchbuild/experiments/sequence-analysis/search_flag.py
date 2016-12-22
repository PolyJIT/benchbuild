#!/usr/bin/env python
"""This module supplies functionality to search for the occurrences of a
certain flag in the generated custom optimization sequences.
"""
import sys
import getopt
import os

__author__ = "Christoph Woller"
__credits__ = ["Christoph Woller"]
__maintainer__ = "Christoph Woller"
__email__ = "wollerch@fim.uni-passau.de"

FILE_PATH = '<filepath_to_results>'
START_OPT_SEQUENCE = 'Optimization Passes'


def search_flag(sequence_file, flag):
    """Searches all programs for the occurrence of a specific flag.

    Args:
        sequence (string): the name of the sequence.
        flag (string): the flag that should be looked for.
    """
    files = []

    for file_name in os.listdir(FILE_PATH + sequence_file + '/'):
        if file_name == '.DS_Store':
            continue

        file = open(FILE_PATH + sequence_file + '/' + file_name, 'r')
        print(file_name)
        sequence = []

        for line in file:
            if START_OPT_SEQUENCE in line:
                rest = line.split('[')[1]
                rest = rest[:len(rest) - 2]
                rest = rest.replace(' ', '')
                rest = rest.replace("'", '')
                sequence = rest.split(',')
                break

        add = True

        for f in sequence:
            if f == ('-' + flag):
                add = False
                break

        if add:
            files.append(file_name)

    print('Flag does not occur in ' + str(len(files)) + ' files:')
    for f in files:
        print(f)


def __usage():
    """Prints out the usage of this python script."""
    print('Wrong usage!\n'
          'Usage: optimize_sequence --experiment=exp --program=prog')


def main(argv):
    """Starts the search process."""
    sequence = None
    flag = None

    try:
        opts, args = getopt.getopt(argv, 'hs:', ['help', 'sequence=', 'flag='])

    except getopt.GetoptError:
        __usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            __usage()
            sys.exit()
        elif opt in ('-s', '--sequence'):
            sequence = arg
        elif opt in '--flag':
            flag = arg
        else:
            __usage()
            sys.exit()

    if flag and sequence:
        search_flag(sequence, flag)
    else:
        __usage()


if __name__ == '__main__':
    main(sys.argv[1:])
