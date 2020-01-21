import logging
import argparse
import subprocess
from subprocess import PIPE, STDOUT

import pandas as pd

from python_tools.workflow_tools import access_plots


def parse_arguments():
    """
    Parse argparse args for module

    :return: args argparse.ArgumentsParser withe parsed args
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--hotspots_table', help='Hotspot table, required', required=True)
    args = parser.parse_args()
    return args


def print_hotspots_table(args):
    """
    Use our table function to print the hotspots table to a PDF

    :return:
    """
    hotspots_table = pd.read_csv(args.hotspots_table, sep='\t')
    hotspots_table.sort_values('Sample', inplace=True)
    logging.info('Generating table for hotspots file: {}'.format(hotspots_table))
    access_plots.table(
        hotspots_table,
        'hotspots',
        output_file_name='hotspots_in_normals.pdf',
        title='Hotspots Found'
    )


def main():
    args = parse_arguments()
    print_hotspots_table(args)


if __name__ == '__main__':
    main()
