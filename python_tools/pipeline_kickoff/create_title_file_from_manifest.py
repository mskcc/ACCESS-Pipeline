import xlrd
import logging
import argparse
import pandas as pd

from ..constants import *


##################################
# Pipeline Kickoff Step #1
#
# This module is used to create a title file with the information needed for a pipeline run
# It is derived from the manually-generated sample manifest
#
# Usage example:
#
# create_title_file_from_manifest \
#   -i ./manifest.xlsx \
#   -o ./title_file.txt


def create_title_file(manifest_file_path, output_filename):
    # Read Manifest as either csv or Excel file
    try:
        manifest = pd.read_csv(manifest_file_path, sep='\t', float_precision='high')
    except (xlrd.biffh.XLRDError, pd.io.common.CParserError):
        manifest = pd.read_excel(manifest_file_path, sep='\t', float_precision='high')
    manifest = manifest.dropna(axis=0, how='all')

    # Select the columns we want from the manifest & rename them
    try:
        title_file = manifest[columns_map.keys()]
    except KeyError as e:
        logging.error('Existing manifest columns:')
        logging.error(manifest.columns)
        raise e

    title_file.columns = columns_map.values()

    # Trim whitespace
    title_file = title_file.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

    # Fix overly-high precision values
    title_file = title_file.round(3)

    # Optionally split by lanes
    if len(title_file[TITLE_FILE__LANE_COLUMN].unique()) > 1:
        for lane in title_file[TITLE_FILE__LANE_COLUMN].unique():
            title_file_sub = title_file[title_file[TITLE_FILE__LANE_COLUMN] == lane]
            # Write title file
            title_file_sub.to_csv('lane-{}_'.format(lane) + output_filename, sep='\t', index=False)
    else:
        title_file.to_csv(output_filename, sep='\t', index=False)

########
# Main #
########

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--manifest_file_path", help="Sample Manifest File (e.g. test_manifest.xlsx)", required=True)
    parser.add_argument("-o", "--output_filename", help="Desired output title location and name", required=True)

    args = parser.parse_args()
    create_title_file(args.manifest_file_path, args.output_filename)


if __name__ == "__main__":
    main()
