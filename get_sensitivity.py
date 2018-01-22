#!/usr/bin/env python

r"""
Merge, compute and correct bias and get the sensitivity all at once. This script runs bias.py, merge.py and sensitivity.py so that you basically don't need to run them.

You need the files to have the same number of trials for each flux to merge them. ntrials.py can be used to determine that.
 """
 
r"""
usage: get_sensitivity.py [-h] [files [files ...]] [--bias [BIAS [BIAS ...]]] [--interp] [--unblinded] [--diagnostic]  [--hide]

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
  --save [filename_extension]
                        Set to save the most useful figures with the 'filename_extension' in their names.
 """

import sys
import argparse
from os import system, remove
from shutil import move


def main(files, bias_files, save_name, options):
    """Get the sensitivity corresponding to the given arguments."""
    if bias_files:
        print '\nFitting of biases to correct'
        for bias_file in bias_files:
            if 'results' in bias_file:
                merged_file = bias_file.replace('results_', 'merged_')
            else:
                merged_file = '/merged_'.join(bias_file.rsplit('/', 1))
            command = 'ipython merge.py -- ' + bias_file + ' ' + merged_file + options['interp']
            # print command
            error = system(command)
            if error:
                exit(0)
            command = 'ipython bias.py -- ' + merged_file + ' ' + bias_file + options['hide'] + bool(save_name)*(" --save "+save_name)
            # print command
            error = system(command)
            if error:
                exit(0)
            system('rm ' + merged_file)

    if files: # Removing bias line from files we do not correct
        for file_ in files:
            temp_file = 'temporary_file.txt'
            with open(temp_file, 'w') as tempfile:
                print 'Removing bias from', file_
                with open(file_) as oldfile:
                    for line in oldfile:
                        if line.find('Bias') == -1:
                            tempfile.write(line)
            remove(file_)
            move(temp_file, file_)

    print '\nMerging and sensitivity'
    error = system('ipython merge.py -- ' + ' '.join(files) + ' ' + ' '.join(bias_files)
                   + ' test_data/merged_all.txt' + options['interp'] + ' --bias' * bool(bias_files) + options['unblinded'] + options['diagnostic'] + bool(save_name)*(" --save "+save_name))
    if error:
        exit(0)
    print 'ipython sensitivity.py -- test_data/merged_all.txt' + options['unblinded'] + options['hide'] + bool(save_name)*(" --save "+save_name)
    error = system('ipython sensitivity.py -- test_data/merged_all.txt' + options['unblinded'] + options['hide'] + bool(save_name)*(" --save "+save_name))
    system('rm test_data/merged_all.txt')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,)

    parser.add_argument(
        "files",
        nargs="*",
        default='',
        type=str,
        help="List of one or more input files to be merged.")

    # Interpolation flag
    parser.add_argument(
        '--interp',
        default=False,
        action="store_true",
        help='Set to interpolate between sample points using splines.'
        ' Leave unset for naive summing at grid points.')

    # Diagnostic flag
    parser.add_argument(
        '--diagnostic',
        default=False,
        action="store_true",
        help='Set to run special diagnostics to visualize results. You may have to force quit the process if you don\'t want to go through all trials.')

    # Bias correction flag
    parser.add_argument(
        '--bias',
        nargs="*",
        default='',
        type=str,
        help='Set to correct bias of the following files.')

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
        help='Set to save the most usefull plots.')

    args = parser.parse_args()
    options = {'interp': ' --interp' * args.interp,
               'diagnostic': ' --diagnostic' * args.diagnostic,
               'hide': ' --hide' * args.hide,
               'unblinded': ' --unblinded' * args.unblinded}
    if args.bias:
        args.interp = True

    if len(sys.argv) >= 2:
        main(args.files, args.bias, args.save, options)
    else:
        parser.print_help()
