# llh-combiner
A project for merging independent 1D maximum likelihood analyses to find a joint maximum likelihood.  Also calculates Neyman (strict) or Feldman&Cousins(TODO) upper limits and sensitivities.
TODO update this when needed.

## get_sensitivity.py
This script has been made to **merge**, **compute and correct bias** and **get the sensitivity** all at once. This script runs bias.py, merge.py and sensitivity.py so that you basically don't need to run them.

You need the files to have the same number of trials for each flux to merge them. ntrials.py can be used to determine that.

##### Usage
```
usage: get_sensitivity.py [-h] [--interp] [--diagnostic] [--bias [BIAS [BIAS ...]]] [--hide] [files [files ...]]

positional arguments:
  files                 List of one or more input files to be merged.

optional arguments:
  -h, --help            show this help message and exit
  --interp              Set to interpolate between sample points using linear interpolation. Leave unset for naive summing at grid points.
  --diagnostic          Set to run special diagnostics to visualize results. You may have to force quit the process if you don't want to go through all trials.
  --bias [BIAS [BIAS ...]]
                        Set to correct bias of the following files.
  --hide                Set to not show the plots.
```

##### Example
```
ipython get_sensitivity.py -- test_data/results_7yrICmuons_KRAg5e7.txt test_data/results_9yrANTshowers_KRAg5e7_2000trials_30sept.txt --bias test_data/results_9yrANTmuons_KRAg5e7_2000trials_30sept.txt --interp --hide
```

### bias.py
Compute the bias of each analysis and write it in the first line of the file so that it can be corrected by merge.py.

### merge.py
For each trial, it sum the log-likelihood ratios of the different analyses (if more than one file given as argument) and fit the flux by maximizing the log-likelihood curve. The output file contains the generated flux, the fitted flux and the maximum of the log-likelihood ratio.
If a bias is written in the first line of an input file, it will correct it. 

### sensitivity.py
Get the sensitivity from the distribution of the fitted fluxes vs generated flux.

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
