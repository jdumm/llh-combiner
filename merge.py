#!/usr/bin/env python

import sys
import math
import numpy as np
from scipy.interpolate import UnivariateSpline

r"""Merge two sets of files representing log-likelihood vs flux. Each trial's original flux, joint best-fit flux, and max TS are written to std output with line break.  Assumes input files will have a header of 3 numbers: minimum flux, maximum flux, number of sample points.  The following lines are assumed to start with the flux and then nsamples of the log-likelihood function.  Option to interpolate between sampling points or use straight sum at sampling points, in which case the flux range and number of sample must match.
"""
# Flux are in units [1/GeV/cm^2/s] or relative to a model
# And TS should be -2*log( likelihood ) [unitless]

def main(infile1, infile2, outputfile, interpolate=False, diagnostic=False):
	try:
		f1 = open(infile1,'r')
		h1 = f1.readline().split() # header

	except IOError: 
		print("Error: Input file {} missing.".format(infile1))
		return 0
	try:
		f2 = open(infile2,'r')
		h2 = f2.readline().split() # header
	except IOError: 
		print("Error: Input file {} missing.".format(infile2))
		return 0
	try:
		of = open(outputfile,'w')
	except IOError:
		print("Error: Unable to open output file {}.".format(outputfile))
		return 0
		

	if ( h1 != h2 and interpolate==False ):
		print('Error: Trying non-interpolation combination of files with different sampling definitions.  Set the --interp flag if desired.')
		return 0

	if(diagnostic):
		import matplotlib.pyplot as plt

	flux_min = float(h1[0])
	flux_max = float(h1[1])
	nsamples = int(h1[2])
	x = np.linspace(flux_min,flux_max,nsamples)
	#padding = (flux_max-flux_min)/float(10)
	padding = 0
	grid_upscale = 12
	xs = np.linspace(flux_min-padding, flux_max+padding, grid_upscale*nsamples) # finer x sampling with slightly extended range for interpolation mode
	#print('flux_min = {}, flux_max = {}, nsamples = {}'.format(flux_min, flux_max, nsamples))
	#print(' with sampling points: {}'.format(x))

	while True: # Loop over the files
		line1 = np.array(map(float,f1.readline().strip().split()))
		line2 = np.array(map(float,f2.readline().strip().split()))
		if len(line1)==0 or len(line2)==0: break # end of file
		if line1[0] != line2[0]:
			print('Error: Fluxes not equal for this trial!') # Maybe need to set an equality tolerance here?
			return 0
		if (interpolate):
			#print 'Finding max by interpolating between grid points...'
		    #spl1 = UnivariateSpline(x, line1[1:], k=2, s=0.5) # k=2nd degree spline, s=smoothing (~chi2)
			spl1 = UnivariateSpline(x, line1[1:], s=0.15)
			spl2 = UnivariateSpline(x, line2[1:], s=0.15)
			# The max is not found to floating pt precision, just on a much finer grid set by grid_upscale.
			sum_array = spl1(xs)+spl2(xs)
			# Find max log-likelihood
			maxllh = np.max(sum_array)
			# Translate max array index into max flux:
			maxflux = np.argmax(sum_array)*((flux_max+padding)-(flux_min-padding))/(grid_upscale*nsamples)
			of.write("{:.2e} {:.2e} {:.2e}\n".format(line1[0],maxflux,maxllh)) # print out flux and the max TS
			if (diagnostic):
				plt.figure()
				plt.plot(x, line1[1:], 'ko', ms=3, alpha=0.5)
				plt.plot(x, line2[1:], 'ko', ms=3, alpha=0.5)
				plt.plot(x, line1[1:]+line2[1:], 'ko', ms=5)
				plt.plot(xs, spl1(xs), 'r', lw=1)
				plt.plot(xs, spl2(xs), 'r', lw=1)
				plt.plot(xs, sum_array, 'r', lw=2)
				ax = plt.gca()
				ymin, ymax = ax.get_ylim()
				plt.plot([maxflux,maxflux],[ymin,ymax], 'g', lw=3)
				plt.show()

		else: # don't interpolate
			#print 'Finding max by summing grid points...'
			sum_array = np.add(line1[1:],line2[1:])
			# Find max log-likelihood
			maxllh = np.max(sum_array)
			# Translate max array index into max flux:
			maxflux = np.argmax(sum_array)*(flux_max-flux_min)/nsamples
			of.write("{:.2e} {:.2e} {:.2e}\n".format(line1[0],maxflux,maxllh)) # print out flux and the max TS

	f1.close()
	f2.close()
	of.close()


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description=__doc__,)

	# Positional arguments for the two input files
	parser.add_argument(
	  "inputfile1",
	  nargs="?",
	  default='',
	  type=str,
	  help="Path to first results input file to be merged")

	parser.add_argument(
	  "inputfile2",
	  nargs="?",
	  default='',
	  type=str,
	  help="Path to second results input file to be merged")

	parser.add_argument(
	  "outputfile",
	  nargs="?",
	  default='merged_output.txt',
	  type=str,
	  help="Path to second results input file to be merged")

	# Interpolation flag
	parser.add_argument(
      '--interp',
      default=False,
      action="store_true",
      help='Set to interpolate between sample points using splines.  Leave unset for naive summing at grid points.')

	# Diagnostic flag
	parser.add_argument(
      '--diagnostic',
      default=False,
      action="store_true",
      help='Set to run special diagnostics to visualize results.  Leave unset for max speed.')

	args = parser.parse_args()
	if (len(sys.argv) >= 3):
		main(args.inputfile1, args.inputfile2, args.outputfile, args.interp, args.diagnostic)
	else:
		parser.print_help()
