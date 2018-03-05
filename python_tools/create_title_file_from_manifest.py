import sys
import pandas as pd


manifest_file_path = sys.argv[1]
title_file_output_filename = sys.argv[2]

manifest = pd.read_excel(manifest_file_path, sep='\t')
# manifest['CMO_SAMPLE_ID'] = manifest['CMO_SAMPLE_ID'].str.replace('Normal', 'Pan_Cancer')

# Split barcode sequences if both are present in single column
manifest['BARCODE_INDEX_1'] = manifest['BARCODE_INDEX'].str.split('-').apply(lambda x: x[0])
manifest['BARCODE_INDEX_2'] = manifest['BARCODE_INDEX'].str.split('-').apply(lambda x: x[1])

relevant_manifest_columns = [
    #     'BARCODE_INDEX',
    'BARCODE_ID',
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

title_file_columns = [
    'Barcode',
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
title_file['Lane'] = title_file['Pool'].str.split('_').apply(lambda x: x[1][-1])

# Correct Barcode Column
title_file['Barcode'] = title_file['Barcode'].str.split('-').apply(lambda x: x[0])

# Write title file
title_file.to_csv(title_file_output_filename, sep='\t', index=False)
