# llh-combiner
A project for merging independent 1D maximum likelihood analyses to find a joint maximum likelihood.  Also calculates Neyman (strict) or Feldman and Cousins(TODO) upper limits and sensitivities.

## File format
The input files are txt files usually named with the prefix results_
They basically contain the llik ratio curves of the pseudo-experiments but also the unblinded results.
They start by the header `min_flux max_flux n_edges` then the data `generated_flux llik_ratio0 llik_ratio1 llik_ratio2...` with `llik_ratio0` corresponding to the loglik ratio of `min_flux`…
The Unblinded results should be added by hand just after the header with the `generated_flux` replaced by `Unblinded`

##### Example
```
0 3 31
Unblinded   0.00e+00	-6.52e-02	-1.35e-01	-2.09e-01...
0.00e+00	0.00e+00	-6.53e-02	-1.34e-01	-2.07e-01...
0.00e+00	0.00e+00	1.53e-02	1.75e-02	8.62e-03...
...
2.50e-01	0.00e+00	-1.07e-02	-2.54e-02	-4.38e-02...
...
5.00e-01	0.00e+00	1.14e-01	2.13e-01	3.00e-01...
...
...
2.00e+00	0.00e+00	-2.69e-02	-5.68e-02	-8.96e-02...
```

The bias.py script will write the bias of this file before the header.

## get_sensitivity.py
One script to run them all!
This script has been made to **merge**, **compute and correct bias** and **get the sensitivity** all at once. This script runs bias.py, merge.py and sensitivity.py so that you basically don't need to run them yourself.

You need the files to have the same number of trials for each flux to merge them. ntrials.py can be used to determine that.

##### Usage
```
usage: get_sensitivity.py [-h] [--bias [BIAS [BIAS ...]]] [--interp] [--unblinded] [--diagnostic]  [--hide] [files [files ...]] 

positional arguments:
  files                 List of one or more input files to be merged.

optional arguments:
  -h, --help            show this help message and exit
  --interp              Set to interpolate between sample points using linear interpolation. Leave unset for naive summing at grid points.
  --diagnostic          Set to run special diagnostics to visualize results. You may have to force quit the process if you don't want to go through all trials.
  --bias [BIAS [BIAS ...]]
                        Set to correct bias of the following files.
  --hide                Set to not show the plots.
  --unblinded           Set to get the p-value of the unblinded data.
```

##### Usage example
```
ipython get_sensitivity.py -- test_data/results_7yrICmuons_KRAg5e7.txt test_data/results_9yrANTshowers_KRAg5e7_2000trials_30sept.txt --bias test_data/results_9yrANTmuons_KRAg5e7_2000trials_30sept.txt --interp --hide
```

### bias.py
Compute the bias of each analysis and write it in the first line of the file so that it can be corrected by merge.py.

### merge.py
For each trial, it sum the log-likelihood ratios of the different analyses (if more than one file given as argument) and fit the flux by maximizing the log-likelihood curve. The output file contains the generated flux, the fitted flux and the maximum of the log-likelihood ratio for each trial and for the unblinded data.
If a bias is written in an input file by the bias.py script, it will correct it. 

### sensitivity.py
Get the sensitivity, but also the p-value and upper limit from the distribution of the fitted fluxes vs generated flux and the unblinded results.

## ntrials.py
If someone hands you a mysterious file, you can use the 'ntrials.py' utility script to determine the number of trials at each flux. This is usefull to merge files with the same number of trials.

##### Usage example
```
ipython ntrials.py -- test_data/results_7yrICmuons_KRAg5e7.txt
```

##### Example output
```
Unique fluxes: [ 0.    0.25  0.5   0.75  1.    1.25  1.5   1.75  2.  ]
For flux = 0.00e+00, nTrials = 2000
For flux = 2.50e-01, nTrials = 2000
...
For flux = 1.75e+00, nTrials = 2000
For flux = 2.00e+00, nTrials = 2000
```

## shuffle.py
The randomized ordering of the trials prior to merging should not matter, provided that there are the right number of trials at the right flux values.  This principle can be verified by shuffling the files and re-running the sensitivity calculation.

##### Usage example
```
ipython shuffle.py -- test_data/results_7yrICmuons_KRAg5e7.txt test_data/results_7yrICmuons_KRAg5e7_shuffled.txt
```

Note that shuffling any input file also groups all trials at the same flux level together in case they are disjoint.  This can be used to bring different files into a common format.
