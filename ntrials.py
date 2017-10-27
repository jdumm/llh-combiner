#!/usr/bin/env python

import sys
import math
import numpy as np

r"""Just open a file and report how many trials take place at each flux value.  Print the results.
"""
# Flux are in units [1/GeV/cm^2/s] or scaling factors relative to a specified model
# And TS should be log( likelihood ) [unitless]

# Returns a list of tuples indicating a range over which the flux is constant
def main(infile):
	try:
		f = open(infile,'r')
		h = f.readline().split() # header
		f.close()
		data = np.loadtxt(infile,skiprows=1)
		order = data[:,0].argsort() # get index based on first column
		data = data[order] # now ordered by flux

	except IOError:
		print "Error: Input file {} missing.".format(infile)
		return 0

	# Identify ranges where fluxes are constant and count trials at each
	unique_fluxes = np.unique(data[:,0])
	prev_flux = data[0][0]
	start_index = 0
	index = 0
	fluxes = []
	count_at_fluxes = []
	for row in data:
		if (row[0] != prev_flux): # found change point
			fluxes.append(prev_flux)
			count_at_fluxes.append(index-start_index)
			start_index = index
		prev_flux = row[0]
		index = index+1
	# Add the last entry:
	fluxes.append(row[0])
	count_at_fluxes.append(len(data[:,0])-start_index)

	print('Unique fluxes: {}'.format(unique_fluxes))
	
	for n in range(len(fluxes)):
		print('For flux = {:0.2e}, nTrials = {}'.format(fluxes[n],count_at_fluxes[n]))


if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description=__doc__,)

	# Positional arguments for the two input files
	parser.add_argument(
	  "inputfile",
	  nargs="?",
	  default='',
	  type=str,
	  help="Path to results input file to be shuffled.")

	args = parser.parse_args()
	if (len(sys.argv) >= 2):
		main(args.inputfile)
	else:
		parser.print_help()
