#!/usr/bin/env python

import sys
import math
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
import numpy as np

r"""Read and display test statistics in sensitivity calculation. Assumes input file has 3 columns: True Flux, Best-fit Flux, and (joint) TS.
"""
# Flux are in units [1/GeV/cm^2/s]
# And TS should be -2*log( likelihood ) [unitless]

def main(infile):
	try:
		data = np.loadtxt(infile)
	except IOError: 
		print "Error: Input file {} missing.".format(infile)
		return 0

	print('Sorted list of unique fluxes:')
	# Find median of the null hypothesis
	ts_null = data[data[:,0]==0.0][:,2] # Isolate the list of all TS values for flux==0
	median_bg = np.median(ts_null)
	print('median of the background-only trials is {}'.format(median_bg))

	unique_fluxes = np.unique(data[:,0]) # sorted
	ps = []
	for flux in unique_fluxes:
		ts = data[data[:,0]==flux][:,2] # Isolate the list of all TS values for this True Flux
		p = float(len(ts[ts>median_bg]))/float(len(ts)) # count how many have TS higher than the median from background
		print('number of entries with flux {} is {} with {}% over the median from background.'.format(flux,len(ts),p*100))
		ps.append(p)
		
	# Find the 90% crossing point using the spline interpolation
	xs = np.linspace(unique_fluxes[0],unique_fluxes[-1:],1000)
	spl = UnivariateSpline(unique_fluxes, ps, s=0.5)
	for x in xs:
		if (spl(x) > 0.9):
			sens = x
			break

	plt.figure()
	plt.plot(unique_fluxes,ps,'ko',ms=5)
	plt.plot(xs,spl(xs),'r',lw=3)
	ax = plt.gca()
	ymin, ymax = ax.get_ylim()
	plt.plot([sens,sens],[ymin,0.9], 'g', lw=2)
	plt.plot([0,sens],[0.9,0.9], 'g', lw=2)
	ax.text(0.95, 0.15, 'Sensitivity: {:0.2f}'.format(sens),
        verticalalignment='top', horizontalalignment='right',
        transform=ax.transAxes,
        color='g', fontsize=18)

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

