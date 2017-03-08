#!/usr/bin/env python

import sys
import math
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import numpy as np

r"""A utility for examining any possible bias in the flux measurement.  Operates on 'merged' input files.
"""

# Flux are in units [1/GeV/cm^2/s] or scaling factors relative to a specified model
# And TS should be -2*log( likelihood ) [unitless]

def main(infile):
	try:
		data = np.loadtxt(infile)
	except IOError: 
		print "Error: Input file {} missing.".format(infile)
		return 0

	plt.figure()
	plt.yscale('log')
	plt.xlabel('Reco Flux - True Flux')
	plt.ylabel('Rate/bin')
	bins=np.arange(-2, 2, 0.25)
	unique_fluxes = np.unique(data[:,0]) # sorted

	print('Sorted list of unique fluxes: {})'.format(unique_fluxes))
	n = len(unique_fluxes)
	meds = np.zeros(n)
	means= np.zeros(n)
	stds = np.zeros(n)
	i = 0
	for tflux in unique_fluxes: # Loop over True Fluxes available
		rflux = data[data[:,0]==tflux][:,1] # Isolate the list of all Reco Flux values for this True Flux
		dist = rflux - tflux
		meds[i] = np.median(dist)
		means[i]= np.mean(dist)
		stds[i] = np.std(dist)
		plt.hist(dist,bins=bins,histtype='step')
		i=i+1

	plt.figure()
	plt.xlabel('True Flux')
	plt.ylabel('Reco Flux - True Flux')
	plt.errorbar(unique_fluxes, meds, xerr=0.0, yerr=0.0)
	plt.errorbar(unique_fluxes, means, xerr=0.0, yerr=stds)
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

	args = parser.parse_args()
	if (len(sys.argv) == 2):
		main(args.inputfile)
	else:
		parser.print_help()

