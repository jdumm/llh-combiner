#!/usr/bin/env python

import sys
import math
import numpy as np
from scipy.interpolate import UnivariateSpline

r"""Merge two sets of files representing log-likelihood vs flux. Each trial's original flux, joint best-fit flux, and max TS are written to std output with line break.  Assumes input files will have a header of 3 numbers: minimum flux, maximum flux, number of sample points.  The following lines are assumed to start with the flux and then nsamples of the log-likelihood function.  Option to interpolate between sampling points or use straight sum at sampling points, in which case the flux range and number of sample must match.
"""
# Flux are in units [1/GeV/cm^2/s] or scaling factors relative to a specified model
# And TS should be -2*log( likelihood ) [unitless]

def main(infile1, infile2, outfile, interpolate=False, diagnostic=False):
	try:
		f1 = open(infile1,'r')
		h1 = f1.readline().split() # header
	except IOError: 
		print("Error: Input file {} missing.".format(infile1))
		return 0

	if(infile2 == 'dummy'): # If 2nd filename is 'dummy', just find the max of the first file.  For testing.
		h2 = h1
	else:
		try:
			f2 = open(infile2,'r')
			h2 = f2.readline().split() # header
		except IOError: 
			print("Error: Input file {} missing.".format(infile2))
			return 0

	try:
		of = open(outfile,'w')
	except IOError:
		print("Error: Unable to open output file {}.".format(outfile))
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
	grid_upscale = 10
	xs = np.linspace(flux_min-padding, flux_max+padding, grid_upscale*nsamples) # finer x sampling with padded range for interpolation mode
	#print('flux_min = {}, flux_max = {}, nsamples = {}'.format(flux_min, flux_max, nsamples))
	#print(' with sampling points: {}'.format(x))

	line_count = 0
	overflow_count = 0
	count_correct = 0
	while True: # Loop over lines in the files
		line1 = np.array(map(float,f1.readline().strip().split()))
		if (infile2 == 'dummy'):
			if len(line1)==0: break # end of file
			line2 = np.zeros(len(line1)) # Set all results of dummy file to 0 - no impact on first analysis
			line2[0] = line1[0] # matching fluxes in dummy file
		else:
			line2 = np.array(map(float,f2.readline().strip().split()))

		if len(line1)==0 or len(line2)==0: break # end of file
		line_count += 1
		if line1[0] != line2[0]:
			print('Error: Fluxes not equal for this trial!') # Maybe need to set an equality tolerance here?
			return 0

		if (interpolate):
			#print('Finding max by interpolating between grid points...')
			# Not sure if we should aim to have this be an option or decide on one method for interpolation
			interp_opt = 'linear'
			#interp_opt = 'spline' 
			if (interp_opt == 'linear'):
				interp1 = np.interp(xs, x, line1[1:])
				interp2 = np.interp(xs, x, line2[1:])
				sum_array = interp1+interp2
			elif (interp_opt == 'spline'):
				# NB: This smoothing factor must be kept very small so that the spline interpolation does not 'miss' the point (0,0).  
				# Otherwise numerical noise near (0,0) dominates the measurement of the median of background-only trials!
				#smoothing_factor = 0.15
				smoothing = 1e-3 # Acts as a maximum chi2 for spline
				order = 2 # degree of spline knob polynomial.  2 or 3 are both suitable.
				interp1 = UnivariateSpline(x, line1[1:], k=order, s=smoothing)
				interp2 = UnivariateSpline(x, line2[1:], k=order, s=smoothing)
				sum_array = interp1(xs)+interp2(xs)
			else:
				print('unrecongized interp_opt: {}'.format(interp_opt))
				return 0

			# Find max log-likelihood
			# The max is not found to floating pt precision, just on a much finer grid set by grid_upscale.
			maxllh = np.max(sum_array)

			# Translate max array index into max flux:
			maxflux = np.argmax(sum_array)*((flux_max+padding)-(flux_min-padding))/(grid_upscale*nsamples)
			if (maxflux > 0.95*(flux_max - flux_min)):
				overflow_count += 1
				#diagnostic = True
			# Check if true flux is contained within 1.0 of the peak (corresponding to 0.5 in log-likelihood ratio).
			for i in range(0,len(sum_array),1):
				if (sum_array[i] > maxllh-1.0):
					lowi = i
					break
			for i in range(len(sum_array)-1,0-1,-1):
				if (sum_array[i] > maxllh-1.0):
					highi = i
					break
			lowflux = lowi*((flux_max+padding)-(flux_min-padding))/(grid_upscale*nsamples)
			highflux = highi*((flux_max+padding)-(flux_min-padding))/(grid_upscale*nsamples)
			trueflux = line1[0]
			#print('{:0.2e} {:0.2e} {:0.2e}'.format(lowflux, trueflux, highflux))
			if (lowflux < trueflux and trueflux < highflux):
				count_correct = count_correct + 1

			of.write("{:.2e} {:.2e} {:.2e}\n".format(trueflux,maxflux,maxllh)) # write the flux and the max TS
			if (diagnostic):
				plt.figure()
				plt.plot(x, line1[1:], 'ko', ms=3, alpha=0.5)
				plt.plot(x, line2[1:], 'ko', ms=3, alpha=0.5)
				plt.plot(x, line1[1:]+line2[1:], 'ko', ms=5)
				if (interp_opt == 'linear'):
					plt.plot(xs, interp1, 'r', lw=1)
					plt.plot(xs, interp2, 'r', lw=1)
				elif (interp_opt == 'spline'):
					plt.plot(xs, interp1(xs), 'r', lw=1)
					plt.plot(xs, interp2(xs), 'r', lw=1)
				else:
					print('unrecongized interp_opt: {}'.format(interp_opt))
					return 0
				plt.plot(xs, sum_array, 'r', lw=2)
				ax = plt.gca()
				ymin, ymax = ax.get_ylim()
				plt.plot([maxflux,maxflux],[ymin,ymax], 'g', lw=3)
				ax.text(0.15, 0.15, '(maxflux, maxllh) = ({:0.2e}, {:0.2e})'.format(maxflux,maxllh),verticalalignment='top', horizontalalignment='left', transform=ax.transAxes, color='g', fontsize=18)
				plt.show()
				#diagnostic = False

		else: # don't interpolate
			#print('Finding max by summing grid points...')
			sum_array = np.add(line1[1:],line2[1:])
			# Find max log-likelihood
			maxllh = np.max(sum_array)
			# Translate max array index into max flux:
			maxflux = np.argmax(sum_array)*(flux_max-flux_min)/nsamples
			if (maxflux > 0.95*(flux_max - flux_min)):
				overflow_count += 1
			of.write("{:.2e} {:.2e} {:.2e}\n".format(line1[0],maxflux,maxllh)) # print out flux and the max TS

	print('Best-fit flux found to be with 5% of the top of the flux range {} a total of {} times out of {}'.format(flux_max,overflow_count,line_count))
	if (interpolate):
		print('True flux contained within 0.5 log-likelihood of the peak in {:0.1f} percent of the trials'.format(100.*count_correct/line_count))
	f1.close()
	if(infile2 != 'dummy'): f2.close()
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
	  help="Path to first results input file to be merged.")

	parser.add_argument(
	  "inputfile2",
	  nargs="?",
	  default='',
	  type=str,
	  help="Path to second results input file to be merged.  Alternatively, 'dummy' can be passed and the first file is processed with no other contributing analysis.")

	parser.add_argument(
	  "outputfile",
	  nargs="?",
	  default='merged_output.txt',
	  type=str,
	  help="Path to output file used to store merged results.")

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
      help='Set to run special diagnostics to visualize results.  Leave unset for usual usage.')

	args = parser.parse_args()
	if (len(sys.argv) >= 3):
		main(args.inputfile1, args.inputfile2, args.outputfile, args.interp, args.diagnostic)
	else:
		parser.print_help()
