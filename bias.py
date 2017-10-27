#!/usr/bin/env python

import sys
import math
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import numpy as np
from scipy.optimize import curve_fit
from os import remove
from shutil import move

r"""A utility for examining any possible bias in the flux measurement.  Operates on 'merged' input files.
"""

# Flux are in units [1/GeV/cm^2/s] or scaling factors relative to a specified model
# And TS should be log( likelihood ) [unitless]


def func(x, a_):
    """Function used to fit the scale factor with a null offset"""
    return a_ * x


def main(infile, datafile, hide=False):
    try:
        data = np.loadtxt(infile)
    except IOError:
        print "Error: Input file {} missing.".format(infile)
        return 0

    plt.figure()
    plt.yscale('log')
    plt.xlabel('Reco Flux - True Flux')
    plt.ylabel('N Trials')
    bins = np.arange(-2, 2, 0.25)
    unique_fluxes = np.unique(data[:, 0])  # sorted
    # unique_fluxes = unique_fluxes[:9]

    print('Sorted list of unique fluxes: {})'.format(unique_fluxes))
    n = len(unique_fluxes)
    ylows = np.zeros(n)
    medsv = np.zeros(n)
    yhighs = np.zeros(n)
    meds = np.zeros(n)
    means = np.zeros(n)
    stds = np.zeros(n)
    i = 0
    rfluxes = []
    stats = []

    for tflux in unique_fluxes:  # Loop over True Fluxes available
        rfluxes.append(data[data[:, 0] == tflux][:, 1])  # Isolate the list of all Reco Flux values for this True Flux
        dist = rfluxes[i] - tflux
        stats = np.percentile(rfluxes[i], [16, 50, 84])
        medsv[i] = stats[1]
        ylows[i] = medsv[i] - stats[0]
        yhighs[i] = stats[2] - medsv[i]
        meds[i] = np.median(dist)
        means[i] = np.mean(dist)
        stds[i] = np.std(dist)
        plt.hist(dist, bins=bins, histtype='step')
        i = i + 1

    param, _ = curve_fit(func, unique_fluxes, medsv)
    fit_a = param[0]
    print 'Bias fitted by: ' + '{0:.3f}'.format(fit_a) + ' * x'

    # Write the bias in the file if datafile is given
    if datafile:
        temp_file = 'temporary_file.txt'
        with open(temp_file, 'w') as tempfile:
            tempfile.write('Bias fitted by: ' + '{0:.3f}'.format(fit_a) + ' * x' + '\n')
            print 'Writing in', datafile[0]
            with open(datafile[0]) as oldfile:
                for line in oldfile:
                    if line.find('Bias') == -1:
                        tempfile.write(line)
        remove(datafile[0])
        move(temp_file, datafile[0])

    plt.figure()
    plt.xlabel('True Flux')
    plt.ylabel('Reco Flux - True Flux')
    plt.errorbar(unique_fluxes, meds, xerr=0.0, yerr=0.0)
    plt.errorbar(unique_fluxes, means, xerr=0.0, yerr=stds)

    plt.figure()
    # plt.xlim(-0.5,3.5)
    # plt.ylim(-0.5,3.5)
    plt.violinplot(rfluxes, unique_fluxes, widths=0.25, showmeans=True, showmedians=False, showextrema=False)
    plt.errorbar(unique_fluxes, medsv, xerr=0.0, yerr=[ylows, yhighs], linestyle='', marker='o', color='k')
    plt.xlabel('True Flux')
    plt.ylabel('Reco Flux')
    x = np.arange(-0.5, np.max(unique_fluxes) + 0.5, 0.1)
    plt.plot(x, x, color='k', linestyle='--')
    fit_y = [fit_a * x_ for x_ in x]
    plt.plot(x, fit_y, color='k', linestyle='-')
    plt.axis('equal')

    plt.figure()
    bins = np.arange(0, 10, 0.5)
    tses = []
    meds_ts = []
    for tflux in unique_fluxes:  # Loop over True Fluxes available
        ts = data[data[:, 0] == tflux][:, 2]  # Isolate the list of all TS values for this True Flux
        tses.append(ts)
        plt.hist(ts, bins, histtype='step')
        meds_ts.append(np.median(ts))
    plt.yscale('log')
    plt.xlabel('TS')

    plt.figure()
    plt.violinplot(tses, unique_fluxes, widths=0.25, showmeans=True, showmedians=False, showextrema=False)
    plt.errorbar(unique_fluxes, meds_ts, xerr=0.0, yerr=0.0, linestyle='', marker='o', color='k')
    plt.xlabel('True Flux')
    plt.ylabel('TS')

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

    # Initial data file where we will write the bias to correct it with merge.py.
    parser.add_argument(
        "datafile",
        nargs="*",
        default='',
        type=str,
        help="Path to file to be merged.",
        metavar="FILE")

# Hide flag
    parser.add_argument(
        '--hide',
        default=False,
        action="store_true",
        help='Set to not show the plots.')

    args = parser.parse_args()
    if (len(sys.argv) >= 2 and len(sys.argv) <= 5):
        main(args.inputfile, args.datafile, args.hide)
    else:
        parser.print_help()
