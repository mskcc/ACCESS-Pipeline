import os
import re
import sys
import argparse
import numpy as np
import pandas as pd
from glob import glob
import ruamel.yaml

# Paths to the default run arguments for testing or runs
from constants import \
    ROOT_DIR, \
    RUN_PARAMS_TEST_PATH, \
    RUN_PARAMS_PATH, \
    FILE_RESOURCES_PATH


##################################
# Pipeline Kickoff Step #2
#
# This module is used to create a yaml file that will be supplied to the pipeline run.
# This yaml file will include three main types of ingredient:
#
#   1. Paths to fastq files and sample sheets
#   2. Paths to resources required during the run (e.g. reference fasta, bed files etc.)
#   3. Values for parameters for the individual tools (e.g. min coverage values, mapq thresholds etc.)
#
# Todo: The main assumption of this module is that the Sample_ID column from the Manifest will have
# sample ids that match the filenames of the fastqs in the data directory. We need to confirm that this will
# always be the case.
#
# Todo: Create check for SampleSheet against indices in Manifest, for BOTH indices, (or for single for now)
# # compare barcodes from title file and $barcodeKeyFile
# expectedBarcode = `grep - w $index $barcodeKeyFile | cut - f
# 2
# `
# actualBarcode = `grep - w $sampleID
# title_file.txt | cut - f
# 1
# `
# echo - e
# "$expectedBarcode and $actualBarcode"
#
# if ["$expectedBarcode" == ""] | | ["$actualBarcode" == ""]
#     then
# echo - e
# "empty barcode."
# echo - e
# "ABORTING"


# Static adapter sequences that surround the barcodes
# Used by the Trimgalore step in the pipeline
#
# Note: These adapters may vary based on the machine and library prep
# Todo: need to confirm these:
# See notes/adapters for full descriptions across all cases
#
ADAPTER_1_PART_1 = 'GATCGGAAGAGCACACGTCTGAACTCCAGTCAC'
ADAPTER_1_PART_2 = 'ATATCTCGTATGCCGTCTTCTGCTTG'
ADAPTER_2_PART_1 = 'AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT'
ADAPTER_2_PART_2 = 'AGATCTCGGTGGTCGCCGTATCATT'

# Template identifier string that will get replaced with the project root location
PIPELINE_ROOT_PLACEHOLDER = '$PIPELINE_ROOT'


def find_files(file_regex, data_dir):
    '''
    Recursively find files in `data_dir` with the given `file_regex`
    '''
    files = [file for folder in os.walk(data_dir) for file in glob(os.path.join(folder[0], file_regex))]
    return files


def load_fastqs(data_dir):
    '''
    Todo: need to support multiple R1 / R2 fastqs per patient?
    Or maybe not b/c "The last segment is always 001":

    https://support.illumina.com/content/dam/illumina-support/documents/documentation/software_documentation/bcl2fastq/bcl2fastq2_guide_15051736_v2.pdf
    Page 19

    :return:
    '''
    fastq1 = find_files('*_R1_001.fastq.gz', data_dir)
    fastq1 = [{'class': 'File', 'path': path} for path in fastq1]
    fastq2 = find_files('*_R2_001.fastq.gz', data_dir)
    fastq2 = [{'class': 'File', 'path': path} for path in fastq2]
    sample_sheet = find_files('SampleSheet.csv', data_dir)
    sample_sheet = [{'class': 'File', 'path': path} for path in sample_sheet]

    return fastq1, fastq2, sample_sheet


def get_adapter_sequences(title_file):
    '''
    Adapter sequences need to be tailored to include each sample barcode from the title file
    GATCGGAAGAGCACACGTCTGAACTCCAGTCAC + bc_1 + ATATCTCGTATGCCGTCTTCTGCTTG
    AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT + bc_2 + AGATCTCGGTGGTCGCCGTATCATT

    These will be used during the Trimgalore adapter trimming step

    :param title_file:
    :return:
    '''
    adapter = ADAPTER_1_PART_1
    adapter += title_file['Barcode_Index_1'].astype(str)
    adapter += ADAPTER_1_PART_2

    adapter2 = ADAPTER_2_PART_1
    adapter2 += title_file['Barcode_Index_2'].astype(str)
    adapter2 += ADAPTER_2_PART_2

    return adapter, adapter2


def contained_in(sample_id, fastq_object):
    '''
    Helper method to sort list of fastqs.
    Returns True if `value` contained in `string`, False otherwise
    '''
    found = sample_id.replace('_', '-') in fastq_object['path'].replace('_', '-')
    if found:
        return 1
    else:
        return 0


def contained_in_fuzzy(sample_id, fastq_object):
    '''
    This method will split the sample ID from the title file, and the fastq filename,
    and find the number of tokens that match between the two. This is used as a backup for when
    the sample name from the title file cannot be matched in any fastq filenames.

    Example:

    Tokens from Sample ID:
    ['PR', 'pt31', 'CF01']

    Will be matched with tokens from fastq file path:
    ['', 'ifs', 'archive', 'BIC', 'share', 'bergerm1', 'JAX',
    '0101', 'BHL5KNBBXX', 'Project', '05500', 'DY', 'Sample',
    'Pan', 'Cancer', 'M6', 'IGO', '05500', 'DY', '46', 'SampleSheet.csv']

    Todo: While this is a neat convience method, we don't have room for errors caused by the following situation:

    This is the correct sample name:
    Sample_Pan_Cancer_F4_IGO_05500_DY_42

    This is not the correct sample name:
    Sample_Pan_Cancer_F4_IGO_05500_DY_43_OTHER_THINGS_not_related_to_samplename_but_happen_to_match

    But it happens to match our filename better...
    Sample_Pan_Cancer_F4_IGO_05500_DY_42_with_some_OTHER_THINGS_that_happen_to_match.fastq.gz

    :param value:
    :param string:
    :return:
    '''
    sample_id_split = re.split('[-_]', sample_id)
    fastq_path_split = re.split('[-_/]', fastq_object['path'])

    new_set = set(sample_id_split) & set(fastq_path_split)
    num_overlapping_tokens = len(list(new_set))
    return num_overlapping_tokens


def get_pos(title_file, fastq_object):
    '''
    Return position of `filename` in 'Sample_ID' column of title_file
    Used for sorting purposes

    :param title_file:
    :param filename:
    :return:
    '''
    boolv = title_file['Sample_ID'].apply(contained_in, fastq_object=fastq_object)

    # If there are no matches, try to match with the fuzzy method:
    if np.sum(boolv) < 1:
        err_string = "Warning, matching patient ID for file {} not found in title file. Using fuzzy match method."
        print >> sys.stderr, err_string.format(fastq_object)
        print >> sys.stderr, "Please check cross check the order of the fastqs in the final inputs.yaml file."
        boolv = title_file['Sample_ID'].apply(contained_in_fuzzy, fastq_object=fastq_object)

    pos = np.argmax(boolv)
    return pos


def sort_fastqs(fastq1, fastq2, sample_sheet, title_file):
    '''
    Helper method to sort fastq paths based on title_file ordering.
    Lists of inputs in our yaml file need to be ordered the same order as each other.
    An alternate method might involve using Record types as a cleaner solution.

    :param fastq1:
    :param fastq2:
    :param sample_sheet:
    :param title_file:
    :return:
    '''
    fastq1 = sorted(fastq1, key=lambda f: get_pos(title_file, f))
    fastq2 = sorted(fastq2, key=lambda f: get_pos(title_file, f))
    sample_sheet = sorted(sample_sheet, key=lambda s: get_pos(title_file, s))
    return fastq1, fastq2, sample_sheet


def include_fastqs_params(fh, data_dir, title_file):
    '''
    Write fastq1, fastq2, read groups and sample_sheet file references to yaml inputs file.

    :param fh:
    :param data_dir:
    :param title_file:
    :return:
    '''
    fastq1, fastq2, sample_sheet = load_fastqs(data_dir)
    fastq1, fastq2, sample_sheet = sort_fastqs(fastq1, fastq2, sample_sheet, title_file)
    perform_checks(fastq1, fastq2, sample_sheet, title_file)

    adapter, adapter2 = get_adapter_sequences(title_file)

    # Note: I put some thought into whether to use a
    # Record type instead of parallel lists here,
    # but ended up not seeing the benefit because certain
    # later steps still require some of the original fields from
    # the record type after the fastqs have been converted to bams.
    # Todo: If there is a way to output a record type then this would be a cleaner option.
    out_dict = {
        'fastq1': fastq1,
        'fastq2': fastq2,
        'sample_sheet': sample_sheet,
        'adapter': adapter.tolist(),
        'adapter2': adapter2.tolist(),

        # Todo: what's the difference between ID & SM?
        # Todo: do we want the whole filename for ID? (see BWA IMPACT logs)
        # or abbreviate it (might be the way they do it in Roslin)
        'add_rg_ID': title_file['Sample_ID'].tolist(),
        'add_rg_SM': title_file['Sample_ID'].tolist(),
        'add_rg_LB': title_file['Lane'].tolist(),

        # Todo: should we use one or two barcodes in the PU field if they are different?
        'add_rg_PU': title_file['Barcode_Index_1'].tolist(),
        'patient_id': title_file['Patient_ID'].tolist()
    }

    fh.write(ruamel.yaml.dump(out_dict))


def include_file_resources(fh, file_resources_path):
    '''
    Write the paths to our resource files into the inputs yaml file.

    :param fh:
    :param file_resources_path:
    :return:
    '''
    with open(file_resources_path, 'r') as stream:
        file_resources = ruamel.yaml.round_trip_load(stream)

    # Substitute in the ROOT_PATH variable based on our current installation directory
    for key in file_resources.keys():
        if 'path' in file_resources[key]:
            new_value = file_resources[key]['path'].replace(PIPELINE_ROOT_PLACEHOLDER, ROOT_DIR)
            file_resources[key]['path'] = new_value

    fh.write(ruamel.yaml.round_trip_dump(file_resources))


def include_run_params(fh, run_params_path):
    # Load and write our default run parameters
    with open(run_params_path, 'r') as stream:
        other_params = ruamel.yaml.round_trip_load(stream)

    fh.write(ruamel.yaml.round_trip_dump(other_params))


def perform_checks(fastq1, fastq2, sample_sheet, title_file):
    '''
    Check whether the title file matches input fastqs

    Todo: we might want an option to remove fastqs or rows from the title_file instead of throwing error,
    in the event that we use this script on a subset of the fastqs in a pool

    :param fastq1:
    :param fastq2:
    :param sample_sheet:
    :param title_file:
    :return:
    '''
    assert len(fastq1) == len(fastq2)
    assert len(sample_sheet) == len(fastq2)
    assert title_file.shape[0] == len(fastq2)


def write_inputs_file(data_dir, title_file, title_file_path, run_params_path, file_resources_path):
    '''
    Start writing our inputs.yaml file

    :param data_dir:
    :param title_file:
    :param title_file_path:
    :param run_params_path:
    :param file_resources_path:
    :return:
    '''
    fh = open('inputs.yaml', 'wb')

    include_fastqs_params(fh, data_dir, title_file)
    include_run_params(fh, run_params_path)
    include_file_resources(fh, file_resources_path)

    # Include title_file in inputs.yaml
    title_file_obj = {'title_file': {'class': 'File', 'path': title_file_path}}
    fh.write(ruamel.yaml.dump(title_file_obj))
    fh.close()


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--title_file_path",
        help="Title File (generated from create_title_file.py)",
        required=True
    )
    parser.add_argument(
        "-d",
        "--data_dir",
        help="Directory with fastqs and samplesheets",
        required=True
    )
    parser.add_argument(
        "-t",
        "--use_test_params",
        help="Whether to run with test params or production params",
        required=False,
        action="store_true"
    )
    return parser.parse_args()


########
# Main #
########

def main():
    args = parse_arguments()

    # Use either the test run parameters, or parameters for a real run
    if args.use_test_params:
        run_params_path = RUN_PARAMS_TEST_PATH
    else:
        run_params_path = RUN_PARAMS_PATH

    # Read title file and load fastqs paths from data directory
    title_file = pd.read_csv(args.title_file_path, sep='\t')

    # Create the inputs file for the run
    write_inputs_file(args.data_dir, title_file, args.title_file_path, run_params_path, FILE_RESOURCES_PATH)


if __name__ == '__main__':
    main()
