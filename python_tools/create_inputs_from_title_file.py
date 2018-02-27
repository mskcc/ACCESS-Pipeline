import os
import sys
import yaml
from glob import glob
import numpy as np
import pandas as pd


# Path to the title file
title_file_path = sys.argv[1]

# Path to directory with fastq files
data_dir = sys.argv[2]


def find_files(file_regex):
    '''
    Recursively find files in folder with given search string
    '''
    files = [file for folder in os.walk(data_dir) for file in glob(os.path.join(folder[0], file_regex))]
    return files


def load_fastqs():
    fastq1 = find_files('*_R1_001.fastq.gz')
    fastq1 = [{'class': 'File', 'path': path} for path in fastq1]
    fastq2 = find_files('*_R2_001.fastq.gz')
    fastq2 = [{'class': 'File', 'path': path} for path in fastq2]
    sample_sheet = find_files('SampleSheet.csv')
    sample_sheet = [{'class': 'File', 'path': path} for path in sample_sheet]

    return fastq1, fastq2, sample_sheet


def get_pos(sample_name):
    '''
    Sort our title_file to match order of samples in data_directory
    '''
    found_boolv = [1 if sample_name.replace('-', '_') in fastq['path'].replace('-', '_') else 0 for fastq in fastq1]
    idx = np.argmax(found_boolv)
    return idx


def write_inputs_file(title_file):
    # Start writing our inputs.yaml file
    out = open('inputs.yaml', 'wb')

    # Adapter sequences need to be tailored to include each sample barcode
    # GATCGGAAGAGCACACGTCTGAACTCCAGTCAC + bc_1 + ATATCTCGTATGCCGTCTTCTGCTTG
    adapter = 'GATCGGAAGAGCACACGTCTGAACTCCAGTCAC'
    adapter += title_file['barcode_index_1'].astype(str)
    adapter += 'ATATCTCGTATGCCGTCTTCTGCTTG'

    # AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT + bc_2 + AGATCTCGGTGGTCGCCGTATCATT
    adapter2 = 'AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT'
    adapter2 += title_file['barcode_index_2'].astype(str)
    adapter2 += 'AGATCTCGGTGGTCGCCGTATCATT'

    out_dict = {
        'fastq1': fastq1,
        'fastq2': fastq2,
        'sample_sheet': sample_sheet,

        'adapter': adapter.tolist(),
        'adapter2': adapter2.tolist(),

        # Todo: what's the difference between ID & SM?
        'add_rg_ID': title_file['Sample_ID'].tolist(),
        'add_rg_SM': title_file['Sample_ID'].tolist(),
        'add_rg_LB': title_file['Lane'].tolist(),

        # Todo: should use one or two barcodes if they are different?
        'add_rg_PU': title_file['barcode_index_1'].tolist(),
    }

    # Load and write our default run parameters
    with open('../resources/run_params.yaml', 'r') as stream:
        other_params = yaml.load(stream)

    out.write(yaml.dump(other_params))
    out.write(yaml.dump(out_dict))
    out.close()


########
# Main #
########

if __name__ == '__main__':
    title_file = pd.read_csv(title_file_path, sep='\t')

    fastq1, fastq2, sample_sheet = load_fastqs()

    # Check the title file matches input fastqs
    assert len(fastq1) == len(fastq2)
    assert len(sample_sheet) == len(fastq1)
    assert title_file.shape[0] == len(fastq1)

    # Apply the sort
    title_file['Sort'] = title_file['Sample_ID'].apply(get_pos)
    title_file = title_file.sort_values('Sort')
    title_file.drop('Sort', axis=1)

    write_inputs_file(title_file)
