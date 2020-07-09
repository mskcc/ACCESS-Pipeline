#!python

'''
@Description : This tool helps to tag hotspot events
@Created :  05/10/2017
@Updated : 10/06/2017
@author : Ronak H Shah, Cyriac Kandoth
'''

from __future__ import division

import re
import sys
import csv
import time
import logging
import argparse


logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.DEBUG)
logger = logging.getLogger('tag_hotspots')

# Use these fields to uniquely identify each mutation
MUTATION_KEYS = [
    'Chromosome',
    'Start_Position',
    'Reference_Allele',
    'Tumor_Seq_Allele2'
]


def parse_arguments():
    """
    Parse arguments for tagging module

    :return:
    """
    parser = argparse.ArgumentParser(prog='tag_hotspots.py', description='This tool helps to tag hotspot events', usage='%(prog)s [options]')
    parser.add_argument('-m', '--input_maf', action='store', dest='input_maf', required=True, type=str, help='Input maf file which needs to be tagged')
    parser.add_argument('-itxt', '--input_hotspot', action='store', dest='input_txt', required=True, type=str, help='Input txt file which has hotspots')
    parser.add_argument('-o','--output_maf', action='store', dest='output_maf', required=True, type=str, help='Output maf file name')
    parser.add_argument('-outdir', '--out_dir', action='store', dest='out_dir', required=False, type=str, help='Full Path to the output dir.')
    args = parser.parse_args()
    return args


def tag_hotspots(args):
    """
    Tagging module entrypoint

    :return:
    """
    logger.info("tag_hotspots: Started the run for tagging hotspots")

    # Load hotspots into a set for easy lookup by chr:pos:ref:alt, and store AA position changed
    hotspots = set()
    with open(args.input_txt, 'rb') as infile:
        reader = csv.DictReader(infile, delimiter='\t')
        for row in reader:
            key = ':'.join([row[k] for k in MUTATION_KEYS])
            hotspots.add(tuple(key))

    # Parse through input MAF, and create a new one with an extra column tagging hotspots
    with open(args.input_maf, 'rb') as infile:
        with open(args.output_maf, 'wb') as outfile:

            # Todo: Comment lines are tossed, though they may need to be retained in some use cases
            filtered_rows = (row for row in infile if not row.startswith('#'))
            reader = csv.DictReader(filtered_rows, delimiter='\t')
            writer = csv.DictWriter(outfile, delimiter='\t', lineterminator='\n', fieldnames=reader.fieldnames + ["hotspot_whitelist"])
            writer.writeheader()

            for row in reader:
                row['hotspot_whitelist'] = 'FALSE'
                key = ':'.join([row[k] for k in MUTATION_KEYS])
                if tuple(key) in hotspots:
                    row['hotspot_whitelist'] = 'TRUE'
                writer.writerow(row)

    logger.info('tag_hotspots: Finished the run for tagging hotspots.')


def main():
    args = parse_arguments()
    tag_hotspots(args)


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()

    totaltime = end_time - start_time
    logging.info('tag_hotspots: Elapsed time was %g seconds', totaltime)
    sys.exit(0)
