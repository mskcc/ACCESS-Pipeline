#!python

"""
@Description : Given a MAF, consolidate complex events that overlap, and remove IGR events
@Created :  05/02/2017
@Updated : 09/12/2018
@author : Ronak H Shah
@author : Tim Song
@author : Cyriac Kandoth
@author : Ian Johnson
"""

from __future__ import division

import os
import sys
import time
import logging
import argparse
import pandas as pd


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.DEBUG)
logger = logging.getLogger('remove_variants')


def main():
    """
    Entrypoint for remove_variants module
    :return:
    """
    parser = argparse.ArgumentParser(prog='remove_variants.py',
                                     description='Consolidate events that overlap, and remove IGR events',
                                     usage='%(prog)s [options]')
    parser.add_argument('-imaf', '--input_maf', action='store', dest='input_maf', required=True, type=str,
                        metavar='SomeID.maf', help='Input maf file which needs to be fixed')
    parser.add_argument('-omaf', '--output_maf', action='store', dest='output_maf', required=True, type=str,
                        metavar='SomeID.maf', help='Output maf file name')
    parser.add_argument('-o', '--out_dir', action='store', dest='out_dir', required=False, type=str,
                        metavar='/somepath/output', help='Full Path to the output dir.')
    args = parser.parse_args()

    logger.info("remove_variants: Started the run for removing simple variants.")

    cvDF, mafDF = read_maf(args)
    posToCheck = make_coordinate_for_complex_variants(cvDF)
    cleanDF = remove_variants(posToCheck, mafDF)
    write_output(args, cleanDF)

    logger.info("remove_variants: Finished the run for removing simple variants.")


def read_maf(args):
    """
    Read the input maf to be filtered. Create additional data frame of Complex variants
    :param args:
    :return:
    """
    df = pd.read_table(args.input_maf, comment='#', low_memory=False)
    complex_variant_df = df.loc[df['TYPE'] == 'Complex']
    return complex_variant_df, df


def make_coordinate_for_complex_variants(cvDF):
    """
    Store the positions of interest to be filtered
    :param cvDF:
    :return:
    """
    positions_to_check = pd.DataFrame(columns=['Chromosome', 'Start'])

    count = 0
    for index, row in cvDF.iterrows():
        chr = row.loc['Chromosome']
        start = row.loc['Start_Position']
        end = row.loc['End_Position']

        for i in range(start, end + 1):
            positions_to_check.loc[count, ['Chromosome', 'Start']] = [chr, i]
            count += 1

    return positions_to_check


def remove_variants(positions_to_check, all_variants_df):
    """
    Remove variants in two cases:
        1. based on overlapping events (I.E. a variant is found to overlap with a complex variant)
        2. Variants intergenic regions (based on Variant_Classification column)
    :param positions_to_check:
    :param all_variants_df:
    :return:
    """
    muts = all_variants_df.copy()
    drop_index = []
    for i_index, i_row in all_variants_df.iterrows():
        m_chr = i_row.loc['Chromosome']
        m_start = i_row.loc['Start_Position']
        m_type = i_row.loc['TYPE']

        if m_type != 'Complex':
            specific_chr_df = positions_to_check.loc[positions_to_check['Chromosome'] == m_chr]
            if (specific_chr_df['Start'] == m_start).any():
                drop_index.append(i_index)

    muts.drop(muts.index[drop_index], inplace=True)

    # Drop mutations in intergenic regions
    muts.drop(muts[muts.Variant_Classification == 'IGR'].index, inplace=True)

    return muts


def write_output(args, output_DF):
    """
    Write the final MAF with variants removed
    :param args:
    :param output_DF:
    :return:
    """
    if args.out_dir:
        out_file = os.path.join(args.out_dir, args.output_maf)
    else:
        out_file = os.path.join(os.getcwd(), args.output_maf)

    output_DF.to_csv(out_file, sep='\t', index=False)


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()

    totaltime = end_time - start_time
    logging.info('remove_variants: Elapsed time was %g seconds', totaltime)
    sys.exit(0)