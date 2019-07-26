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

    parser.add_argument('--bioinfo_utils', help='sample ids, required', required=True)
    parser.add_argument('--java', help='path to BioinfoUtils jar, required', required=True)
    parser.add_argument('--sample_ids', nargs='+', help='sample ids, required', required=True)
    parser.add_argument('--sample_classes', nargs='+', help='sample classes, required', required=True)
    parser.add_argument('--unfiltered_pileups', nargs='+', help='unfiltered pileups, required', required=True)
    parser.add_argument('--duplex_pileups', nargs='+', help='duplex pileups, required', required=True)
    parser.add_argument('--hotspot_list', help='hotspot list, required', required=True)

    args = parser.parse_args()
    return args


def create_file_of_pileups(args):
    """
    Print the following file:

    sample_id   sample_class    path_to_pileup
    sample_id   sample_class    path_to_pileup
    sample_id   sample_class    path_to_pileup

    path_to_pileup is duplex for Tumor, unfiltered for Normal

    :param args:
    :return:
    """
    def duplex_or_unfiltered_pileup(row):
        if row['sample_class'] == 'Tumor':
            return args.duplex_pileups[row.name]
        elif row['sample_class'] == 'Normal':
            return args.unfiltered_pileups[row.name]
        else:
            raise 'Invalid sample_class {} for sample {}'.format(row.sample_class, row.name)

    pileups_df = pd.DataFrame({'sample_id': args.sample_ids, 'sample_class': args.sample_classes})
    pileups_df['pileup'] = pileups_df.apply(duplex_or_unfiltered_pileup, axis=1)
    # Reorder columns
    pileups_df = pileups_df[['sample_id', 'sample_class', 'pileup']]
    pileups_df.to_csv('pileups.tsv', sep='\t', header=False, index=False)


def call_bioinfo_utils(args):
    """
    Create and call command to run hotspots genotyping module

    :param args:
    :return:
    """
    cmd = [
        args.java,
        '-server',
        '-Xms4g',
        '-Xmx4g',
        '-cp',
        args.bioinfo_utils,
        'org.mskcc.juber.commands.FindHotspotsInNormals',
        'pileups.tsv',
        args.hotspot_list
    ]
    cmd = ' '.join(cmd)

    logging.info('Calling command: {}'.format(cmd))
    print('CMD: ' + cmd)

    p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    print('CMD output: {}'.format(p.stdout.read()))


def print_hotspots_table():
    """
    Use our table function to print the hotspots table to a PDF

    :return:
    """
    print('here1')
    hotspots_table = pd.read_csv('hotspots-in-normals.txt', sep='\t')
    print('here2')
    logging.info('Generating table for hotspots file: {}'.format(hotspots_table))
    print('here3')
    access_plots.table(hotspots_table, 'hotspots', output_file_name='hotspots_in_normals.pdf')
    print('here4')


def main():
    args = parse_arguments()
    create_file_of_pileups(args)
    call_bioinfo_utils(args)
    print_hotspots_table()


if __name__ == '__main__':
    main()
