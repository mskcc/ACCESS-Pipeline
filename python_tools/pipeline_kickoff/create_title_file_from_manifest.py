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
#   -o ./DY_title_file.txt
#
# Note: The following requirements will be imposed on the input manifest file:
#
# 1. The "SAMPLE_CLASS" column must contain entries specified as either "Tumor" or "Normal"
# 2. The "CMO_SAMPLE_ID" column must contain entries that match at least partially with the fastq file paths
# 3. The "CMO_PATIENT_ID" column must match between Tumor and Normal samples
# 4. There must be at least one Normal for Sample for each Tumor sample


# Todo: Start filling these out in manifest?
# These are normally not found in the manifest, and will be supplied as dashes
MISSING_COLUMNS = [
    'PatientName',
    'MAccession',
    'Extracted_DNA_Yield'
]


def create_title_file(manifest_file_path, title_file_output_filename):
    # Read Manifest as either csv or Excel file
    try:
        manifest = pd.read_csv(manifest_file_path, sep='\t')
    except (xlrd.biffh.XLRDError, pd.io.common.CParserError):
        manifest = pd.read_excel(manifest_file_path, sep='\t')
    manifest = manifest.dropna(axis=0, how='all')

    # Sometimes we require some additional fixing of our columns.
    # Uncomment next line to apply change to MANIFEST__CMO_SAMPLE_ID_COLUMN.
    # manifest[MANIFEST__CMO_SAMPLE_ID_COLUMN] = manifest[MANIFEST__CMO_SAMPLE_ID_COLUMN].str.replace('Normal', 'Pan_Cancer')

    # Select the columns we want from the manifest & rename them
    title_file = manifest.loc[:,columns_map.keys()]
    title_file.columns = columns_map.values()

    # Include any missing columns
    for col in MISSING_COLUMNS:
        title_file.loc[:,col] = '-'

    # Get Lane # from Pool column
    # We use this new column to group the QC results by lane
    # Todo: have a lane column manually entered
    title_file.loc[:,TITLE_FILE__LANE_COLUMN] = title_file.loc[:,TITLE_FILE__POOL_COLUMN].str.split('_').apply(lambda x: x[1][-1]).copy()

    # Write title file
    title_file.to_csv(title_file_output_filename, sep='\t', index=False)


########
# Main #
########

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--manifest_file_path", help="Sample Manifest File (see runs/DY/manifest.xlsx)", required=True)
    parser.add_argument("-o", "--output_filename", help="Desired output title location and name", required=True)

    args = parser.parse_args()
    create_title_file(args.manifest_file_path, args.output_filename)


if __name__ == "__main__":
    main()
