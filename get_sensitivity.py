#!/usr/bin/env python

"""Run automatically the scripts to get the sensitivity with or without correction of the biases
 instead of running yourself each script."""

import sys
import argparse
from os import system, remove
from shutil import move

def main(files, bias_files, options):
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
            command = 'ipython bias.py -- ' + merged_file + ' ' + bias_file + options['hide']
            # print command
            error = system(command)
            if error:
                exit(0)
            system('rm ' + merged_file)

    # Removing bias line from files we do not correct
    if files:
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
           + ' test_data/merged_all.txt' + options['interp'] + ' --bias' * bool(bias_files) + options['diagnostic'])
    if error:
        exit(0)
    error = system('ipython sensitivity.py -- test_data/merged_all.txt' + options['hide'])
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
        help='Set to run special diagnostics to visualize results.  Leave unset for usual usage.')

    # Bias correction flag
    parser.add_argument(
        '--bias',
        nargs="*",
        default='',
        type=str,
        help='Set to correct bias of the following files. Leave unset for usual usage.')

    # Hide flag
    parser.add_argument(
        '--hide',
        default=False,
        action="store_true",
        help='Set to not show the plots.')

    args = parser.parse_args()
    options = {'interp': ' --interp' * args.interp,
               'diagnostic': ' --diagnostic' * args.diagnostic,
               'hide': ' --hide' * args.hide}

    if len(sys.argv) >= 2:
        main(args.files, args.bias, options)
    else:
        parser.print_help()
