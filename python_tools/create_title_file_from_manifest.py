import sys
import warnings
import subprocess
import numpy as np
import pandas as pd


warnings.filterwarnings('ignore')
pd.options.display.max_columns = 999

manifest = pd.read_csv('./Project_05500_DY_title_file.txt', sep='\t')
manifest['CMO_SAMPLE_ID'] = manifest['CMO_SAMPLE_ID'].str.replace('Normal', 'Pan_Cancer')

# Get the correct order of the fastq files from the IGO output directory
fastq_output_dir = sys.argv[1]
ordered_fastqs = subprocess.Popen('find {} | grep R1_001.fastq.gz'.format(fastq_output_dir))

# Sort samples from manifest as per sorting in IGO output directory
def get_pos(x):
    x_rep = x.replace('-', '_')
    idx = np.argmax([1 if x_rep in y.replace('-', '_') else 0 for y in ordered_fastqs])
    return idx

# Apply the sort
manifest['Sort'] = manifest['CMO_SAMPLE_ID'].apply(get_pos)
manifest = manifest.sort_values('Sort')

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
title_file.to_csv('/Users/johnsoni/Desktop/Project_05500_DY_title_file.txt', sep='\t', index=False)
