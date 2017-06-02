#!/usr/bin/env python

import sys
import math
from re import match
import numpy as np
from scipy.interpolate import UnivariateSpline

r"""Merge two sets of files representing log-likelihood vs flux. Each trial's original flux, joint best-fit flux, and max TS are written to std output with line break.  Assumes input files will have a header of 3 numbers: minimum flux, maximum flux, number of sample points.  The following lines are assumed to start with the flux and then nsamples of the log-likelihood function.  Option to interpolate between sampling points or use straight sum at sampling points, in which case the flux range and number of sample must match.
"""
# Flux are in units [1/GeV/cm^2/s] or scaling factors relative to a specified model
# And the joint TS should be -2*log( likelihood ) [unitless]

def main(files, interpolate=False, diagnostic=False, bias=False):
	infiles = files[:-1] # All but the last argument are input files
	outfile = files[-1]  # Last argument is the output file
	n_in = len(infiles)
	fs = [] # input file handles
	hs = [] # headers
	bs = [] # bias
	for infile in infiles:
		try:
			fs.append( open(infile,'r') ) # keep a list of the open files
			hs.append(fs[-1].readline().split()) # append header of the last file opened...
			if 'Bias' in hs[-1]:				 # ... if the first line is the bias, get the header from the second line.
				bs.append(hs.pop()) # append bias of the last file opened
				hs.append(fs[-1].readline().split())
				if bias:
					print 'Correction of bias for', infile
			else:
				bs.append(['Bias', 'fitted', 'by:', '1', '*', 'x', '+', '0']) # If no bias in the file, put no bias
		except IOError:
			print("Error: Input file {} cannot be opened.".format(infile))
			return 0
	try:
		of = open(outfile,'w')
	except IOError:
		print("Error: Unable to open output file {}.".format(outfile))
		return 0

	for header in hs: # Check that all headers match the first file
		if ( header != hs[0] and interpolate==False):
			print('Error: Trying non-interpolation combination of files with different sampling definitions.  Set the --interp flag if desired.')
			return 0

	if(diagnostic):
		import matplotlib.pyplot as plt

	flux_min = float(hs[0][0])
	flux_max = float(hs[0][1])
	nsamples = int(hs[0][2])
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
	end_of_file = False
	while True: # Loop over lines in the files
		line_count += 1
		lines = []
		for f in fs:
			line = np.array(map(float,f.readline().strip().split()))
			lines.append(line)
			if len(line) == 0:
				end_of_file=True # end of at least one file (trailing lines in other files ignored)
				break
			if line[0] != lines[0][0]: # Check that all fluxes for this trial are equal to the first file
				print('Error: Fluxes not equal for this trial!') # Maybe need to set an equality tolerance here?
				return 0
		if end_of_file == True:
			break # Break out of outer loop over lines in file

		if (interpolate):
			a_ = []
			b_ = []
			for index in range(len(bs)):
				a_.append(float(bs[index][3]))
				b_.append(float(bs[index][7]))
			#print('Finding max by interpolating between grid points...')
			# Not sure if we should aim to have this be an option or decide on one method for interpolation
			interp_opt = 'linear'
			# interp_opt = 'fit_poly'
			# interp_opt = 'spline'
			sum_array = np.zeros(len(xs))
			interps = []
			if interp_opt == 'fit_poly':
				for index, line in enumerate(lines):
					if bias:
						fit = np.polyfit((x - b_[index]) / a_[index], line[1:], deg=5)
					else:
						fit = np.polyfit(x, line[1:], deg=5)
					y_offset = np.polyval(fit, [0])
					interp = np.polyval(fit, xs) - y_offset
					interps.append(interp)
					sum_array += interp
			elif (interp_opt == 'linear'):
				for index, line in enumerate(lines):
					if bias:
						interp = np.interp(xs, (x - b_[index]) / a_[index], line[1:])
					else:
						interp = np.interp(xs, x, line[1:])
					interps.append(interp)
					sum_array += interp
			elif (interp_opt == 'spline'):
				# NB: This smoothing factor must be kept very small so that the spline interpolation does not 'miss' the point (0,0).
				# Otherwise numerical noise near (0,0) dominates the measurement of the median of background-only trials!
				#smoothing_factor = 0.15
				smoothing = 1e-3 # Acts as a maximum chi2 for spline
				order = 2 # degree of spline knob polynomial.  2 or 3 are both suitable.
				for index, line in enumerate(lines):
					if bias:
						spline = UnivariateSpline((x - b_[index]) / a_[index], line[1:], k=order, s=smoothing)
					else:
						spline = UnivariateSpline(x, line[1:], k=order, s=smoothing)
					interps.append(spline)
					sum_array += spline(xs)
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
			trueflux = lines[0][0]
			#print('{:0.2e} {:0.2e} {:0.2e}'.format(lowflux, trueflux, highflux))
			if (lowflux < trueflux and trueflux < highflux):
				count_correct = count_correct + 1

			of.write("{:.2e} {:.2e} {:.2e}\n".format(trueflux,maxflux,maxllh)) # write the flux and the max TS
			if diagnostic:# and maxflux != 0:
				plt.figure()
				for interp in interps:
					plt.plot(xs, interp, 'r', lw=1.2, alpha=0.7)
				plt.plot(xs, sum_array, 'r', lw=2.7)
				coarse_sum_array = np.zeros(len(lines[0][1:]))
				for line in lines:
					plt.plot(x, line[1:], 'ko', ms=3, alpha=0.6)
					coarse_sum_array += line[1:]
				plt.plot(x, coarse_sum_array, 'ko', ms=5)
				ax = plt.gca()
				ymin, ymax = ax.get_ylim()
				plt.plot([maxflux,maxflux],[ymin,ymax], 'g', lw=3)
				ax.text(0.15, 0.15, '(max flux, max llh) = ({:0.2e}, {:0.2e})'.format(maxflux,maxllh),verticalalignment='top', horizontalalignment='left', transform=ax.transAxes, color='g', fontsize=18)
				plt.show()
				#diagnostic = False

		else: # don't interpolate
			#print('Finding max by summing grid points...')
			sum_array = np.zeros(len(lines[0][1:]))
			for line in lines:
				sum_array += line[1:]
			# Find max log-likelihood
			maxllh = np.max(sum_array)
			# Translate max array index into max flux:
			maxflux = np.argmax(sum_array)*(flux_max-flux_min)/nsamples
			if (maxflux > 0.95*(flux_max - flux_min)):
				overflow_count += 1
			of.write("{:.2e} {:.2e} {:.2e}\n".format(lines[0][0],maxflux,maxllh)) # print out flux and the max TS

	print('Best-fit flux found to be with 5% of the top of the flux range {} a total of {} times out of {}'.format(flux_max,overflow_count,line_count))
	if (interpolate):
		print('True flux contained within 0.5 log-likelihood of the peak in {:0.1f} percent of the trials'.format(100.*count_correct/line_count))
	for f in fs:
		f.close()
	of.close()


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description=__doc__,)

	# Positional arguments for the N input files and 1 output file.
	parser.add_argument(
	  "files",
	  nargs="*",
	  default='',
	  type=str,
	  help="List of one or more input files to be merged followed by the single output file name.  At least two arguments required.")

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

	# Bias correction flag
	parser.add_argument(
      '--bias',
      default=False,
      action="store_true",
      help='Set to correct bias from a datafile output of bias.py. Leave unset for usual usage.')

	args = parser.parse_args()
	if (len(sys.argv) >= 2 and len(args.files) >= 2):
		main(args.files, args.interp, args.diagnostic, args.bias)
	else:
		parser.print_help()
