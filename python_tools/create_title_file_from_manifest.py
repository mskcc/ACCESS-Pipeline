import sys
import xlrd
import pandas as pd
import warnings

warnings.filterwarnings('ignore')


# Usage:
#
# python create_title_file_from_manifest.py <path to manifest> <output_title_file_name>
manifest_file_path = sys.argv[1]
title_file_output_filename = sys.argv[2]

# Read Manifest as either csv or Excel file
try:
    manifest = pd.read_csv(manifest_file_path, sep='\t')
except (xlrd.biffh.XLRDError, pd.io.common.CParserError):
    manifest = pd.read_excel(manifest_file_path, sep='\t')

#
# manifest['CMO_SAMPLE_ID'] = manifest['CMO_SAMPLE_ID'].str.replace('Normal', 'Pan_Cancer')

# Split barcode sequences if both are present in single column
manifest['BARCODE_INDEX_1'] = manifest['BARCODE_INDEX'].astype(str).str.split('-').apply(lambda x: x[0])
manifest['BARCODE_INDEX_2'] = manifest['BARCODE_INDEX'].astype(str).str.split('-').apply(lambda x: x[1])

# The following relevant columns will be used in the pipeline,
# and printed in the QC report
relevant_manifest_columns = [
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

title_file_columns = [
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

# Todo: what to do when following columns aren't included in manifest?
missing_columns = [
    'Collab_ID',
    'PatientName',
    'MAccession',
    'Extracted_DNA_Yield'
]

# Select the columns we want from the manifest & rename them
title_file = manifest[relevant_manifest_columns]
title_file.columns = title_file_columns

# Include any missing columns
for col in missing_columns:
    title_file[col] = '-'

# Get Lane # from Pool column
# We use this new column to group the QC results by lane
title_file['Lane'] = title_file['Pool'].str.split('_').apply(lambda x: x[1][-1])

# Correct Barcode Column
title_file['Barcode'] = title_file['Barcode'].str.split('-').apply(lambda x: x[0])

# Write title file
title_file.to_csv(title_file_output_filename, sep='\t', index=False)
