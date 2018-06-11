import xlrd
import argparse
import pandas as pd

from ..constants import *


##################################
# Pipeline Kickoff Step #1
#
# This module is used to create a title file with the information needed for a pipeline run
# It is derived from the manually-curated sample manifest
#
# Usage example:
#
# create_title_file_from_manifest \
#   -i ./manifest.xlsx \
#   -o ./title_file.txt
#
# Note: The following requirements will be imposed on the input manifest file:
#
# 1. The fields that are found in the sample manifest should matched with the examples in test/test_data
# 2. The sample ID's in the manifest must be matched somewhere in the fastq file names fom the -d data folder
# 3. The sample ID's in the manifest must be matched somewhere in the path to the SampleSheet.csv files
# 4. The SAMPLE_CLASS column of the manifest must consist of the values either "Tumor" or "Normal"
# 5. Each "Tumor" sample must have at least one associated "Normal" sample
# 6. Each sample folder in the -d data folder must have these three files:
#
# '_R1_001.fastq.gz'
# '_R2_001.fastq.gz'
# 'SampleSheet.csv'


def create_title_file(manifest_file_path, title_file_output_filename):
    # Read Manifest as either csv or Excel file
    try:
        manifest = pd.read_csv(manifest_file_path, sep='\t')
    except (xlrd.biffh.XLRDError, pd.io.common.CParserError):
        manifest = pd.read_excel(manifest_file_path, sep='\t')
    manifest = manifest.dropna(axis=0, how='all')

    # Select the columns we want from the manifest & rename them
    title_file = manifest[columns_map.keys()]
    title_file.columns = columns_map.values()

    # Trim whitespace
    title_file = title_file.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

    # Write title file
    title_file.to_csv(title_file_output_filename, sep='\t', index=False)


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
