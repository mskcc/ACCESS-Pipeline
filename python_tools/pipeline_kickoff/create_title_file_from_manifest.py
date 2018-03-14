import xlrd
import argparse
import pandas as pd
import warnings

warnings.filterwarnings('ignore')


# The following relevant columns will be used in the pipeline,
# and printed in the QC report
RELEVANT_MANIFEST_COLUMNS = [
    #     'BARCODE_INDEX',
    'BARCODE_ID',
    'BARCODE_INDEX_1',
    'BARCODE_INDEX_2',
    'CAPTURE_NAME',
    #     'CMO_SAMPLE_ID',
    'INVESTIGATOR_SAMPLE_ID',
    #     'CMO_PATIENT_ID',
    'INVESTIGATOR_PATIENT_ID',
    'SAMPLE_CLASS',
    'SAMPLE_TYPE',
    'LIBRARY_INPUT[ng]',
    'LIBRARY_YIELD[ng]',
    'CAPTURE_INPUT[ng]',
    'CAPTURE_BAIT_SET',
    'SEX'
]

# They^ will be given the following new names

# Note: adapted from make-title-file-from-manifest.sh:
#
# Barcode
# Pool
# Sample_ID
# Collab_ID
# Patient_ID
# Class
# Sample_type
# Input_ng
# Library_yield
# Pool_input
# Bait_version
# Gender
# PatientName
# MAccession
# Extracted_DNA_Yield

TITLE_FILE_COLUMNS = [
    'Barcode',
    'Barcode_Index_1',
    'Barcode_Index_2',
    'Pool',
    'Sample_ID',
    'Patient_ID',
    'Class',
    'Sample_type',
    'Input_ng',
    'Library_yield',
    'Pool_input',
    'Bait_version',
    'Gender'
]

# Todo: Why aren't these in the manifest?
MISSING_COLUMNS = [
    'Collab_ID',
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

    # Sometimes we require some additional finagling of our columns
    # manifest['CMO_SAMPLE_ID'] = manifest['CMO_SAMPLE_ID'].str.replace('Normal', 'Pan_Cancer')

    # Split barcode sequences if both are present in single column
    manifest['BARCODE_INDEX_1'] = manifest['BARCODE_INDEX'].astype(str).str.split('-').apply(lambda x: x[0])
    manifest['BARCODE_INDEX_2'] = manifest['BARCODE_INDEX'].astype(str).str.split('-').apply(lambda x: x[1])

    # Select the columns we want from the manifest & rename them
    title_file = manifest[RELEVANT_MANIFEST_COLUMNS]
    title_file.columns = TITLE_FILE_COLUMNS

    # Include any missing columns
    for col in MISSING_COLUMNS:
        title_file[col] = '-'

    # Get Lane # from Pool column
    # We use this new column to group the QC results by lane
    title_file['Lane'] = title_file['Pool'].str.split('_').apply(lambda x: x[1][-1])

    # Correct Barcode Column
    title_file['Barcode'] = title_file['Barcode'].str.split('-').apply(lambda x: x[0])

    # Write title file
    title_file.to_csv(title_file_output_filename, sep='\t', index=False)


########
# Main #
########

if __name__ == "__main__":
    # Usage:
    #
    # python create_title_file_from_manifest.py <path to manifest> <output_title_file_name>
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--manifest_file_path", help="Sample Manifest File (see runs/DY/manifest.xlsx)", required=True)
    parser.add_argument("-o", "--output_filename", help="Desired output title location and name", required=True)

    args = parser.parse_args()
    create_title_file(args.manifest_file_path, args.output_filename)
