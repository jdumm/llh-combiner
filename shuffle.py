#!/usr/bin/env python

import sys
import math
import numpy as np
import random as ran
import copy

r"""Shuffle a scrambled-trial results file to simpy re-order for later merging.  It serves as a crosscheck that the order of the trials does not matter.  Since a file is expected to have multiple trials at many flux values, the flux change indices are found.  Shuffling only occurs inside of these ranges.  Shuffle.py sorts the entries before shuffling to account for disjoint trials where trials from some flux values are scattered throughout the file.
"""
# Flux are in units [1/GeV/cm^2/s] or scaling factors relative to a specified model
# And TS should be -2*log( likelihood ) [unitless]

# Returns a list of tuples indicating a range over which the flux is constant
def find_change_indices(idata):
	unique_fluxes = np.unique(idata[:,0])
	prev_flux = idata[0][0]
	start_index = 0
	index = 0
	change_points = []
	for row in idata:
		if (row[0] != prev_flux): # found change point
			change_points.append([start_index,index-1])
			start_index = index
		prev_flux = row[0]
		index = index+1
	change_points.append([start_index,len(idata)-1]) # last range
	print("Found these ranges of constant flux: {}".format(change_points))
	return change_points

# Shuffle each range of the text file where the flux is constant
# This got a little ugly requiring the deepcopy...
def shuffle(idata, odata, r): # r is a tuple (low-, high-index) for a given flux range
	# This array maps the original index in idata to a new index in odata
	mapping = range(r[0],r[1]+1)
	ran.shuffle(mapping)
	index=0
	for n in range(r[0],r[1]+1):
		odata[n] = idata[mapping[index]]
		index = index+1
	return odata
	

def main(infile, outfile):
	try:
		f = open(infile,'r')
		h = f.readline().split() # header
		f.close()
		idata = np.loadtxt(infile,skiprows=1)
		order = idata[:,0].argsort() # get index based on first column
		idata = idata[order] # now ordered by flux
		odata = copy.deepcopy(idata) # shuffled output
	except IOError:
		print "Error: Input file {} missing.".format(infile)
		return 0

	# Identify ranges where fluxes are constant
	change_points = find_change_indices(idata)

	# Now shuffle inside of the individual flux ranges
	for r in change_points:
		shuffle(idata, odata, r)
		
	#np.savetxt(outfile, odata, header=str(h.split()))
	try:
		np.savetxt(outfile, odata,fmt='%0.2e', header='{} {} {}'.format(h[0],h[1],h[2]), comments='')
	except IOError:
		print("Error: Unable to open output file {}.".format(outfile))
		return 0


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

	parser.add_argument(
	  "outputfile",
	  nargs="?",
	  default='shuffled_output.txt',
	  type=str,
	  help="Path to output file used to store shuffled results.")

	args = parser.parse_args()
	if (len(sys.argv) >= 2):
		main(args.inputfile, args.outputfile)
	else:
		parser.print_help()
