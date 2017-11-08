#!/usr/bin/env python

r"""
Shuffle a scrambled-trial results file to simply re-order for later merging.  It serves as a crosscheck that the order of the trials does not matter.  Since a file is expected to have multiple trials at many flux values, the flux change indices are found.  Shuffling only occurs inside of these ranges.  Shuffle.py sorts the entries before shuffling to account for disjoint trials where trials from some flux values are scattered throughout the file.
"""

r"""
usage: shuffle.py [-h] [inputfile] [outputfile]

positional arguments:
  inputfile   Path to results input file to be shuffled.
  outputfile  Path to output file used to store shuffled results.

optional arguments:
  -h, --help  show this help message and exit
"""
# Flux are in units [1/GeV/cm^2/s] or scaling factors relative to a specified model
# And TS should be log( likelihood ) [unitless]

import argparse
import sys
import numpy as np

# Returns a list of tuples indicating a range over which the flux is constant


def find_change_indices(data):
    """
    Find the line where the generated flux changes.
    """
    prev_flux = data[0][0]
    start_index = 0
    index = 0
    change_points = []
    for row in data:
        if row[0] != prev_flux:  # found change point
            change_points.append([start_index, index])
            start_index = index
        prev_flux = row[0]
        index = index + 1
    change_points.append([start_index, len(data)])  # last range
    print "Found these ranges of constant flux: {}".format(change_points)
    return change_points


def main(infile, outfile):
    """
    Shuffle the trials.
    """
    try:
        f = open(infile, 'r')
        h = f.readline().split()  # header
        f.close()
        data = np.loadtxt(infile, skiprows=1)
        order = data[:, 0].argsort()  # get index based on first column
        data = data[order]  # now ordered by flux
    except IOError:
        print "Error: Input file {} missing.".format(infile)
        return 0

    # Identify ranges where fluxes are constant
    change_points = find_change_indices(data)

    # Now shuffle inside of the individual flux ranges
    for r in change_points:
        subarray = data[r[0]:r[1]]  # slice it and assign to a shallow copy
        np.random.shuffle(subarray)  # editing 'subarray' edits the original 'data'

    try:
        np.savetxt(outfile, data, fmt='%0.2e', header='{} {} {}'.format(h[0], h[1], h[2]), comments='')
    except IOError:
        print "Error: Unable to open output file {}.".format(outfile)
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,)

    # Positional arguments for the two input files
    parser.add_argument(
        "inputfile",
        nargs="?",
        default='',
        type=str,
        help="Path to results input file to be shuffled.")

    parser.add_argument(
        "outputfile",
        nargs="?",
        default='shuffled_output.txt',
        type=str,
        help="Path to output file used to store shuffled results.")

    args = parser.parse_args()
    if len(sys.argv) >= 2:
        main(args.inputfile, args.outputfile)
    else:
        parser.print_help()
