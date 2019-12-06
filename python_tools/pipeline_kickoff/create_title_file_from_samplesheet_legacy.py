import xlrd
import logging
import argparse
import pandas as pd

from ..legacy_constants import *

##################################
# Pipeline Kickoff Step #1
#
# This module is used to create a title file with the information needed for a pipeline run
# It is derived from the manually-curated sample samplesheet
#
# Usage example:
#
# create_title_file_from_samplesheet \
#   -i ./SampleSheet.csv \
#   -o ./title_file.txt
#
# Note: The following requirements will be imposed on the input samplesheet file:
#
# 1. The fields that are found in the sample samplesheet should matched with the examples in test/test_data
# 2. The sample ID's in the samplesheet must be matched somewhere in the fastq file names fom the -d data folder
# 3. The sample ID's in the samplesheet must be matched somewhere in the path to the SampleSheet.csv files
# 4. The SAMPLE_CLASS column of the samplesheet must consist of the values either "Tumor" or "Normal"
# 5. Each "Tumor" sample must have at least one associated "Normal" sample
# 6. Each sample folder in the -d data folder must have these three files:
#
# '_R1_001.fastq.gz'
# '_R2_001.fastq.gz'
# 'SampleSheet.csv'


def create_title_file(samplesheet_file_path, output_filename):
    # Read samplesheet as either csv or Excel file
    try:
        samplesheet = pd.read_csv(samplesheet_file_path, sep=',')
    except (xlrd.biffh.XLRDError, pd.io.common.CParserError):
        samplesheet = pd.read_excel(samplesheet_file_path, sep=',')
    
    samplesheet = samplesheet.dropna(axis=0, how='all')
    samplesheet = samplesheet.replace('\n','', regex=True)
    samplesheet[SAMPLE_SHEET__COLLAB_ID_COLUMN] = "DMP"
    samplesheet[SAMPLE_SHEET__SAMPLE_TYPE_COLUMN] = "Plasma"
    samplesheet[SAMPLE_SHEET__INPUT_NG_COLUMN] = "-"
    samplesheet[SAMPLE_SHEET__LIBRARY_INPUT_COLUMN] = "-"
    samplesheet[SAMPLE_SHEET__LIBRARY_YIELD_COLUMN] = "-"
    samplesheet[SAMPLE_SHEET__POOL_INPUT_COLUMN] = "-"
    samplesheet[SAMPLE_SHEET__BAIT_VERSION_COLUMN] = "MSK-ACCESS-v1_0"
    samplesheet[SAMPLE_SHEET__CAPTURE_INPUT_COLUMN] = "-"
    samplesheet[SAMPLE_SHEET__CAPTURE_BAIT_SET_COLUMN] = "-"
    samplesheet[SAMPLE_SHEET__SEX_COLUMN] = "F"
    
    # Select the columns we want from the samplesheet & rename them
    try:
        title_file = samplesheet[columns_map_samplesheet.keys()]
    except KeyError as e:
        logging.error('Existing samplesheet columns:')
        logging.error(samplesheet.columns)
        raise e

    title_file.columns = columns_map_samplesheet.values()

    # Trim whitespace
    title_file = title_file.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

    # Optionally split by lanes
    if len(title_file[TITLE_FILE__LANE_COLUMN].unique()) > 1:
        duplicate_samples = []
        for lane in title_file[TITLE_FILE__LANE_COLUMN].unique():
            duplicate_samples.extend(title_file[title_file[TITLE_FILE__LANE_COLUMN] == lane][TITLE_FILE__SAMPLE_ID_COLUMN].tolist())
        duplicate_samples = list(filter(lambda x: duplicate_samples.count(x)>1,duplicate_samples))
        columns_to_consider = title_file.columns.tolist()
        columns_to_consider.remove(TITLE_FILE__LANE_COLUMN)
        title_file = title_file.drop_duplicates(subset=columns_to_consider)
        title_file[TITLE_FILE__LANE_COLUMN].loc[title_file[TITLE_FILE__SAMPLE_ID_COLUMN].isin(duplicate_samples)] = 0
        # Write title file
        # title_file_sub.to_csv('lane-{}_'.format(lane) + output_filename, sep='\t', index=False)
        title_file.to_csv(output_filename, sep='\t', index=False)
    else:
        title_file.to_csv(output_filename, sep='\t', index=False)

########
# Main #
########

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--samplesheet_file_path", help="Sample Manifest File (e.g. test_samplesheet.xlsx)", required=True)
    parser.add_argument("-o", "--output_filename", help="Desired output title location and name", required=True)

    args = parser.parse_args()
    create_title_file(args.samplesheet_file_path, args.output_filename)


if __name__ == "__main__":
    main()
