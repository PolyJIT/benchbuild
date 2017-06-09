#!/usr/bin/env python
"""This module supplies functionality to convert a csv file into a LaTeX table.
"""
import os
import csv

__author__ = "Christoph Woller"
__credits__ = ["Christoph Woller"]
__maintainer__ = "Christoph Woller"
__email__ = "wollerch@fim.uni-passau.de"

PATH = '<your path>'


def csv_to_tex():
    """Creates a tex tables for each csv file in the specified folder and
    stores these tables in corresponding tex files.
    """
    for file_name in os.listdir(PATH):
        if file_name.endswith(".csv"):
            name = os.path.splitext(file_name)[0]
            dest_name = name + '.tex'
            dest = open(PATH + '/' + dest_name, 'wb')
            reader = csv.reader(open(PATH + '/' + file_name, 'r'))

            parts = name.split('_')
            label = ''
            caption = ''

            for i in range(len(parts)):
                if i == 0:
                    label = parts[i]
                else:
                    caption += (parts[i] + str(' '))

            dest.write(bytes('\\begin{center}\n', 'UTF-8'))
            dest.write(bytes('\\begin{longtable}[h!]', 'UTF-8'))

            first = True

            for row in reader:
                if first:
                    dest.write(bytes('{', 'UTF-8'))
                    for i in range(len(row)):
                        dest.write(bytes('l', 'UTF-8'))
                        if i < len(row) - 1:
                            dest.write(bytes('|', 'UTF-8'))
                    dest.write(bytes('}\n', 'UTF-8'))

                for i in range(len(row)):
                    if i == 0:
                        dest.write(bytes(row[i], 'UTF-8'))
                    else:
                        dest.write(bytes('&' + row[i], 'UTF-8'))

                dest.write(bytes('\\\\\n', 'UTF-8'))
                if first:
                    dest.write(bytes('\hline\n', 'UTF-8'))
                    first = False

            dest.write(bytes('\\caption{' + caption + '}\n', 'UTF-8'))
            dest.write(bytes('\\label{tab:' + label + '}\n', 'UTF-8'))
            dest.write(bytes('\\end{longtable}\n', 'UTF-8'))
            dest.write(bytes('\\end{center}\n', 'UTF-8'))


def main():
    """Starts the conversion from csv files to tex files."""
    csv_to_tex()


if __name__ == '__main__':
    main()
