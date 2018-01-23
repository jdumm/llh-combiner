#!/usr/bin/env python

r"""
Read and display test statistics in sensitivity calculation. Assumes input file has 3 columns: True Flux, Best-fit Flux, and TS.

"""

r"""
usage: sensitivity.py [-h] [--hide] [--unblinded] [--save [SAVE]] [FILE]

positional arguments:
  FILE           Path to input file containing results of (pre-merged)
                 scrambled trials.

optional arguments:
  -h, --help     show this help message and exit
  --hide         Set to not show the plots.
  --unblinded    Set to get the p-value of the unblinded data.
  --save [SAVE]  Set to save the most usefull plots with SAVE as a filename
                 extension.
"""
# Flux are in units [1/GeV/cm^2/s] or scaling factors relative to a specified model
# And TS should be log( likelihood ) [unitless]

import sys
import argparse
import matplotlib.pyplot as plt
import scipy
# from scipy.interpolate import UnivariateSpline
from scipy.optimize import leastsq
import numpy as np


def main(infile, hide, unblinded, save_name):
    try:
        data = np.loadtxt(infile)
    except IOError:
        print "Error: Input file {} missing.".format(infile)
        return 0

    # Find median of the null hypothesis
    ts_null = data[data[:, 0] == 0.0][:, 2]  # Isolate the list of all TS values for flux==0
    median_bg = np.median(ts_null)
    print 'median of the background-only trials is {}'.format(median_bg)

    plt.figure()
    plt.yscale('log')
    plt.xlabel('TS')
    plt.ylabel('Density probability')
    bin_width = 0.2
    bins = np.arange(0, 10, bin_width)
    flux_unblinded = 0
    ts_unblinded = 0
    ul = 0. # upper limit

    if unblinded:
        if data[0, 0] != -1:
            print "Error: no unblinded results in", infile
            exit(0)
        flux_unblinded = data[0, 1]
        ts_unblinded = data[0, 2]
        data = data[1:]

        p_value = float(len(ts_null[ts_null > ts_unblinded])) / float(len(ts_null))

    unique_fluxes = np.unique(data[:, 0])  # sorted
    print 'Sorted list of unique fluxes: {})'.format(unique_fluxes)
    ps = []
    cl = [] # Confidence level: probability to have a test statistic larger than ts_unblinded
    for flux in unique_fluxes:
        ts = data[data[:, 0] == flux][:, 2]  # Isolate the list of all TS values for this True Flux
        if flux == 0.:
            plt.hist(ts, bins, normed=True, cumulative=-1, histtype='step', color='r', lw=2, label='Background')

            if unblinded:
                plt.plot([ts_unblinded, ts_unblinded], [0., p_value], 'g', lw=2)
                plt.plot([0, ts_unblinded], [p_value, p_value], 'g', lw=2, label='p-value: {:0.2f}'.format(p_value))

        if flux == 1.:
            plt.hist(ts, bins, normed=True, cumulative=True, histtype='step', color='b', lw=2, label='Model flux')
            ax = plt.gca()
            ax.legend(loc='lower center')
            if save_name:
                plt.savefig('plots/TS_distrib_'+save_name+'.pdf')
        p = float(len(ts[ts > median_bg])) / float(len(ts))  # count how many have TS higher than the median from background
        if unblinded:
            cl.append(float(len(ts[ts > ts_unblinded])) / float(len(ts)))
        print 'number of entries with flux {} is {} with {}% over the median from background.'.format(flux, len(ts), p * 100)
        ps.append(p)

    xs = np.linspace(unique_fluxes[0], unique_fluxes[-1:], 1000)
    # Find the 90% crossing point using the spline interpolation for sensitivity
    # spl_ps = UnivariateSpline(unique_fluxes, ps, k=3, s=0.1)
    # for x in xs:
    #     if spl_ps(x) > 0.9:
    #         sens = x
    #         break

    # Find the 90% crossing point fitting with erf
    fitfunc = lambda p, x: scipy.special.erf(p[0]*x+p[1]) # 1-np.exp(p[0]*x+p[1]))*p[2] # Target function
    errfunc = lambda p, x, y: fitfunc(p, x) - y # Distance to the target function
    p0 = [1., 1.] # Initial guess for the parameters
    p1, _ = leastsq(errfunc, p0[:], args=(unique_fluxes, ps))
    # plt.plot(unique_fluxes, ps, 'ko', xs, fitfunc(p1, xs), "r-", ms=5, lw=3) # Plot of the data and the fit

    for x in xs:
        if fitfunc(p1, x) > 0.9:
            sens = x
            break

    print '\nSensitivity is: {:0.3f}'.format(sens)

    if unblinded:
        # Find the 90% crossing point using the spline interpolation for upper limit
        # spl_cl = UnivariateSpline(unique_fluxes, cl, k=3, s=0.1)
        # for x in xs:
        #     if spl_cl(x) > 0.9:
        #         ul = x
        #         break

        # Find the 90% crossing point fitting with erf
        p2, _ = leastsq(errfunc, p0[:], args=(unique_fluxes, cl))

        for x in xs:
            if fitfunc(p2, x) > 0.9:
                ul = x
                break

        plt.figure()
        plt.xlabel('Flux')
        plt.ylabel('Fraction with TS > unblinded TS')
        # plt.plot(unique_fluxes, cl, 'ko', ms=5)
        # plt.plot(xs, fitfunc(p2, xs), 'r', lw=3)
        plt.plot(unique_fluxes, cl, 'ko', xs, fitfunc(p2, xs), 'r', ms=5, lw=3) # Plot of the data and the fit
        ax = plt.gca()
        ymin, _ = ax.get_ylim()
        plt.plot([ul, ul], [ymin, 0.9], 'g', lw=2)
        plt.plot([0, ul], [0.9, 0.9], 'g', lw=2)
        ax.text(0.95, 0.15, 'Upper limit: {:0.2f}'.format(ul),
                verticalalignment='top', horizontalalignment='right',
                transform=ax.transAxes,
                color='g', fontsize=18)
        if save_name:
            plt.savefig('plots/UpperLimit_'+save_name+'.pdf')

        print 'Fitted flux is', flux_unblinded
        print 'p-value is', p_value * 100, '%'
        print 'Upper limit at 90% confidence level is {:0.2f}'.format(ul)

    plt.figure()
    plt.xlabel('Flux')
    plt.ylabel('Fraction with TS > background median')
    # plt.plot(unique_fluxes, ps, 'ko', ms=5)
    # plt.plot(xs, spl_ps(xs), 'r', lw=3)
    plt.plot(unique_fluxes, ps, 'ko', xs, fitfunc(p1, xs), 'r', ms=5, lw=3) # Plot of the data and the fit
    ax = plt.gca()
    ymin, _ = ax.get_ylim()
    plt.plot([sens, sens], [ymin, 0.9], 'g', lw=2)
    plt.plot([0, sens], [0.9, 0.9], 'g', lw=2)
    ax.text(0.95, 0.15, 'Sensitivity: {:0.2f}'.format(sens),
            verticalalignment='top', horizontalalignment='right',
            transform=ax.transAxes,
            color='g', fontsize=18)
    if save_name:
        plt.savefig('plots/Sensitivity_'+save_name+'.pdf')
    if not hide:
        plt.show()


if __name__ == "__main__":
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

    # Unblinded flag
    parser.add_argument(
        '--unblinded',
        default=False,
        action="store_true",
        help='Set to get the p-value of the unblinded data.')

    # Plot saving flag
    parser.add_argument(
        '--save',
        nargs="?",
        default='',
        type=str,
        help='Set to save the most usefull plots with SAVE as a filename extension.')

    args = parser.parse_args()
    if len(sys.argv) >= 2 and len(sys.argv) <= 6:
        main(args.inputfile, args.hide, args.unblinded, args.save)
    else:
        parser.print_help()
