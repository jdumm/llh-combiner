#!/usr/bin/env python

r"""
Read and display test statistics in sensitivity calculation. Assumes input file has 3 columns: True Flux, Best-fit Flux, and TS.

usage: sensitivity.py [-h] [--hide] [FILE]

positional arguments:
  FILE        Path to input file containing results of (pre-merged) scrambled trials.

optional arguments:
  -h, --help  show this help message and exit
  --hide      Set to not show the plots.
"""
# Flux are in units [1/GeV/cm^2/s] or scaling factors relative to a specified model
# And TS should be log( likelihood ) [unitless]

import sys
import math
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import numpy as np

def main(infile, hide):
    try:
        data = np.loadtxt(infile)
    except IOError:
        print "Error: Input file {} missing.".format(infile)
        return 0

    # Find median of the null hypothesis
    ts_null = data[data[:, 0] == 0.0][:, 2]  # Isolate the list of all TS values for flux==0
    median_bg = np.median(ts_null)
    print('median of the background-only trials is {}'.format(median_bg))

    plt.figure()
    plt.yscale('log')
    plt.xlabel('TS')
    plt.ylabel('Rate/bin')
    bins = np.arange(0, 10, 1)
    unique_fluxes = np.unique(data[:, 0])  # sorted
    print('Sorted list of unique fluxes: {})'.format(unique_fluxes))
    ps = []
    for flux in unique_fluxes:
        ts = data[data[:, 0] == flux][:, 2]  # Isolate the list of all TS values for this True Flux
        plt.hist(ts, bins, histtype='step')
        p = float(len(ts[ts > median_bg])) / float(len(ts))  # count how many have TS higher than the median from background
        print('number of entries with flux {} is {} with {}% over the median from background.'.format(flux, len(ts), p * 100))
        ps.append(p)

    # Find the 90% crossing point using the spline interpolation
    xs = np.linspace(unique_fluxes[0], unique_fluxes[-1:], 1000)
    spl = UnivariateSpline(unique_fluxes, ps, k=3, s=0.1)
    for x in xs:
        if (spl(x) > 0.9):
            sens = x
            break
    print('\nSensitivity is: {:0.3f}'.format(sens))

    plt.figure()
    plt.xlabel('Flux')
    plt.ylabel('Fraction with TS > background median')
    plt.plot(unique_fluxes, ps, 'ko', ms=5)
    plt.plot(xs, spl(xs), 'r', lw=3)
    ax = plt.gca()
    ymin, ymax = ax.get_ylim()
    plt.plot([sens, sens], [ymin, 0.9], 'g', lw=2)
    plt.plot([0, sens], [0.9, 0.9], 'g', lw=2)
    ax.text(0.95, 0.15, 'Sensitivity: {:0.2f}'.format(sens),
            verticalalignment='top', horizontalalignment='right',
            transform=ax.transAxes,
            color='g', fontsize=18)
    if not hide:
        plt.show()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__,)

    parser.add_argument(
        "inputfile",
        nargs="?",
        default='',
        type=str,
        help="Path to input file containing results of (pre-merged) scrambled trials.",
        metavar="FILE")

# Hide flag
    parser.add_argument(
        '--hide',
        default=False,
        action="store_true",
        help='Set to not show the plots.')

    args = parser.parse_args()
    if (len(sys.argv) == 2 or len(sys.argv) == 3):
        main(args.inputfile, args.hide)
    else:
        parser.print_help()
