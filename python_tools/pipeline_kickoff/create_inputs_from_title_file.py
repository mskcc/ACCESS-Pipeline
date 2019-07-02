import sys
import pprint
import argparse
import ruamel.yaml
import numpy as np
import pandas as pd

# constants include the paths to the config files
from python_tools.constants import *
from python_tools.util import (
    DELIMITER,
    INPUTS_FILE_DELIMITER,
    get_pos,
    reverse_complement,
    all_strings_are_substrings,
    include_yaml_resources,
    include_version_info
)


##################################
# Pipeline Kickoff Step #2
#
# Usage Example:
#
# create_inputs_from_title_file \
#   -i ./XX_title_file.txt \
#   -d ./Innovation-Pipeline/test/test_data/new_test_data
#
# This module is used to create a yaml file that will be supplied to the pipeline run.
#
# This yaml file will include three main types of ingredient:
#
#   1. Paths to fastq files and sample sheets
#   2. Paths to resources required during the run (e.g. reference fasta, bed files etc.)
#   3. Values for parameters for the individual tools (e.g. min coverage values, mapq thresholds etc.)
#
# The requirements for running this module include:
#
#   1. Read 1 fastq, Read 2 fastq, and SampleSheet.csv are found in the same directory
#   2. The Sample ID from the title_file matches with at least some part of the path in the fastq files and sample sheet
#   3. The Patient ID from the title_file is found in at least one of the fastq files
#
# Todo: This file is too large



# Strings to target when looking for Illumina run files
#
# Todo: need to support multiple R1 / R2 fastqs per patient?
# Or maybe not b/c "The last segment is always 001":
# https://support.illumina.com/content/dam/illumina-support/documents/documentation/software_documentation/bcl2fastq/bcl2fastq2_guide_15051736_v2.pdf (Page 19)
#
FASTQ_1_FILE_SEARCH = '_R1_001.fastq.gz'
FASTQ_2_FILE_SEARCH = '_R2_001.fastq.gz'
SAMPLE_SHEET_FILE_SEARCH = 'SampleSheet.csv'

ADAPTER_1 = 'GATCGGAAGAGC'
ADAPTER_2 = 'AGATCGGAAGAGC'


def load_fastqs(data_dir):
    """
    Recursively find all sample files in `data_dir`

    Note:
    os.walk yields a 3-list (dirpath, dirnames, filenames)

    Todo: Consider building a scalable Sample Class to hold all data related to each sample

    :param data_dir: str - folder of Samples with fastqs and SampleSheet.csv
    """
    # Gather Sample Sub-directories (but leave out the parent dir)
    folders = list(os.walk(data_dir, followlinks=True))

    # Filter to those that contain a read 1, read 2, and sample sheet
    folders_2 = filter(lambda folder: any([FASTQ_1_FILE_SEARCH in x for x in folder[2]]), folders)
    folders_3 = filter(lambda folder: any([FASTQ_2_FILE_SEARCH in x for x in folder[2]]), folders_2)
    folders_4 = filter(lambda folder: any([SAMPLE_SHEET_FILE_SEARCH in x for x in folder[2]]), folders_3)

    # Issue a warning if not all folders had necessary files (-1 to exclude topmost directory)
    if not len(folders) - 1 == len(folders_4):
        print(DELIMITER + 'Warning, some samples may not have a Read 1, Read 2, or sample sheet. '
                          'Please manually check inputs.yaml')
        print('All sample folders:')
        pprint.pprint(folders)
        print('Sample folders with correct result files:')
        pprint.pprint(folders_4)

    # Take just the files
    files_flattened = [os.path.join(dirpath, f) for (dirpath, dirnames, filenames) in folders_4 for f in filenames]

    # Separate into three lists
    fastq1 = filter(lambda x: FASTQ_1_FILE_SEARCH in x, files_flattened)
    fastq1 = [{'class': 'File', 'path': path} for path in fastq1]
    fastq2 = filter(lambda x: FASTQ_2_FILE_SEARCH in x, files_flattened)
    fastq2 = [{'class': 'File', 'path': path} for path in fastq2]
    sample_sheet = filter(lambda x: SAMPLE_SHEET_FILE_SEARCH in x, files_flattened)
    sample_sheet = [{'class': 'File', 'path': path} for path in sample_sheet]

    return fastq1, fastq2, sample_sheet


def perform_duplicate_barcodes_check(title_file):
    """
    Check that no two samples have the same barcode 1 or barcode 2

    Note that this only works when performing this check on an individual lane,
    as barcodes may be reused across lanes.
    """
    for lane in title_file[MANIFEST__LANE_COLUMN].unique():
        lane_subset = title_file[title_file[MANIFEST__LANE_COLUMN] == lane]

        if np.sum(lane_subset[MANIFEST__BARCODE_INDEX_1_COLUMN].duplicated()) > 0:
            raise Exception(DELIMITER + 'Duplicate barcodes for barcode 1, lane {}. Exiting.'.format(lane))

        if np.sum(lane_subset[MANIFEST__BARCODE_INDEX_2_COLUMN].duplicated()) > 0:
            raise Exception(DELIMITER + 'Duplicate barcodes for barcode 2, lane {}. Exiting.'.format(lane))


def sort_fastqs(fastq1, fastq2, sample_sheet, title_file):
    """
    Helper method to sort fastq paths based on title_file ordering.
    Lists of inputs in our yaml file need to be ordered the same order as each other.
    An alternate method might involve using Record types as a cleaner solution.
    """
    fastq1 = sorted(fastq1, key=lambda f: get_pos(title_file, f))
    fastq2 = sorted(fastq2, key=lambda f: get_pos(title_file, f))
    sample_sheet = sorted(sample_sheet, key=lambda s: get_pos(title_file, s))
    return fastq1, fastq2, sample_sheet


def remove_missing_samples_from_title_file(title_file, fastq1, title_file_path):
    """
    If samples IDs from title file aren't found in data directory,
    issue a warning and remove them from the title file

    # Todo: Should we instead raise an error and not continue?
    """
    found_boolv = np.array([any([sample in f['path'] for f in fastq1]) for sample in title_file[MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN]])
    samples_not_found = title_file.loc[~found_boolv, MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN]

    if samples_not_found.shape[0] > 0:
        print(DELIMITER + 'Error: The following samples were missing either a read 1 fastq, read 2 fastq, or sample sheet. ' +
                          'These samples will be removed from the title file so that the remaining samples can be run.')
        print('Please perform a manual check on the inputs file before running the pipeline.')
        print(samples_not_found)

    # Todo: Refactor to put title_file info into inputs.yaml --> then no need to use original title_file in pipeline
    title_file = title_file.loc[found_boolv, :]
    title_file.to_csv(title_file_path, sep='\t', index=False)
    return title_file


def remove_missing_fastq_samples(fastq1, fastq2, sample_sheet, title_file):
    """
    If a sample ID from the title file is not found in any of the paths to the fastqs, remove it from the title file.

    Todo: For the SampleSheet files, this relies on the parent folder containing the sample name
    """
    fastq1 = filter(lambda f: any([sid in f['path'] for sid in title_file[MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN]]), fastq1)
    fastq2 = filter(lambda f: any([sid in f['path'] for sid in title_file[MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN]]), fastq2)
    sample_sheet = filter(lambda s: any([sid in s['path'] for sid in title_file[MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN]]), sample_sheet)

    return fastq1, fastq2, sample_sheet


def check_i5_index(title_file_i5, sample_sheet_i5):
    """
    The i5 index (or "Index2" in the SampleSheet.csv file) will either match as is, or as a reverse-complement,
    based on the machine the sequencing was done on.

    :param title_file_i5:
    :param sample_sheet_i5:
    :return:
    """
    rev_comp_i5_barcode = reverse_complement(sample_sheet_i5)

    i5_matches_non_reverse_complemented = sample_sheet_i5 == title_file_i5
    i5_matches_reverse_complemented = rev_comp_i5_barcode == title_file_i5

    err_string = 'i5 index from title file {} does not match i5 index from SampleSheet {}. Aborting.' \
        .format(title_file_i5, sample_sheet_i5)

    assert i5_matches_non_reverse_complemented or i5_matches_reverse_complemented, err_string

    if i5_matches_non_reverse_complemented:
        return NON_REVERSE_COMPLEMENTED
    elif i5_matches_reverse_complemented:
        return REVERSE_COMPLEMENTED


def perform_barcode_index_checks_i5(title_file, sample_sheets):
    """
    The i5 index (or "Index2" in the SampleSheet.csv file) will either match as is, or as a reverse-complement,
    based on the machine the sequencing was done on.

    :param title_file:
    :param sample_sheets:
    :return:
    """
    i5_sequencer_types = []
    for sample_id in title_file[MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN]:
        cur_sample = title_file[title_file[MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN] == sample_id]

        matching_sample_sheets = [s for s in sample_sheets if sample_id in s.get('path')]
        assert len(matching_sample_sheets) == 1, 'Incorrect matching sample sheet count for sample {}'.format(sample_id)
        sample_sheet = matching_sample_sheets[0]
        sample_sheet_df = pd.read_csv(sample_sheet['path'], sep=',')

        try:
            sample_sheet_i5 = sample_sheet_df['Index2'].values[0]
        except KeyError:
            print('Index2 not found in SampleSheet.csv. Skipping i5 barcode index validation.')
            return

        title_file_i5 = cur_sample[MANIFEST__BARCODE_INDEX_2_COLUMN].values[0]
        i5_sequencer_types.append(check_i5_index(title_file_i5, sample_sheet_i5))

    all_non_reverse_complemented = all([match_type == NON_REVERSE_COMPLEMENTED for match_type in i5_sequencer_types])
    all_reverse_complemented = all([match_type == REVERSE_COMPLEMENTED for match_type in i5_sequencer_types])

    assert all_non_reverse_complemented or all_reverse_complemented, 'Not all barcodes followed same i5 index scheme'

    if all_non_reverse_complemented:
        print(DELIMITER + 'All i5 barcodes match without reverse-complementing, sequencer was one of the following:')
        print('NovaSeq\nMiSeq\nHiSeq2500')

    elif all_reverse_complemented:
        print(DELIMITER + 'All i5 barcodes match after reverse-complementing, sequencer was one of the following:')
        print('HiSeq4000\nMiniSeq\nNextSeq')


def perform_barcode_index_checks_i7(title_file, sample_sheets):
    """
    Confirm that the barcode indexes in the title file,
    match to what is listed in the Sample Sheet files from the Illumina Run

    :param title_file:
    :param sample_sheets:
    :return:
    """
    for sample_id in title_file[MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN]:
        cur_sample = title_file[title_file[MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN] == sample_id]
        title_file_i7 = cur_sample[MANIFEST__BARCODE_INDEX_1_COLUMN].values[0]

        matching_sample_sheets = [s for s in sample_sheets if sample_id in s.get('path')]
        assert len(matching_sample_sheets) == 1, 'Incorrect matching sample sheet count for sample {}'.format(sample_id)
        sample_sheet = matching_sample_sheets[0]
        sample_sheet_df = pd.read_csv(sample_sheet['path'], sep=',')

        # i7 Sequence should always match
        sample_sheet_i7 = sample_sheet_df['Index'].values[0]

        err_template = 'i7 index does not match for sample {}. Aborting. {} != {}'
        err_string = err_template.format(sample_id, sample_sheet_i7, title_file_i7)
        assert sample_sheet_i7 == title_file_i7, err_string


def include_fastqs_params(fh, data_dir, title_file, title_file_path, force):
    """
    Write fastq1, fastq2, read group identifiers and sample_sheet file references to yaml inputs file.

    :param fh:
    :param data_dir:
    :param title_file:
    :param title_file_path:
    :param force:
    """
    # Load and sort our data files
    fastq1, fastq2, sample_sheets = load_fastqs(data_dir)
    # Get rid of data files that don't have an entry in the title_file
    fastq1, fastq2, sample_sheets = remove_missing_fastq_samples(fastq1, fastq2, sample_sheets, title_file)
    # Get rid of entries from title file that are missing data files
    title_file = remove_missing_samples_from_title_file(title_file, fastq1, title_file_path)
    # Sort everything based on the ordering in the title_file
    fastq1, fastq2, sample_sheets = sort_fastqs(fastq1, fastq2, sample_sheets, title_file)

    if not force:
        # Check that we have the same number of everything
        perform_length_checks(fastq1, fastq2, sample_sheets, title_file)
        # Check the barcode sequences in the title_file against the sequences in the sample_sheets
        perform_barcode_index_checks_i7(title_file, sample_sheets)
        perform_barcode_index_checks_i5(title_file, sample_sheets)

    samples_info = {
        'fastq1': fastq1,
        'fastq2': fastq2,
        'sample_sheet': sample_sheets,
        'adapter': [ADAPTER_1] * len(fastq1),
        'adapter2': [ADAPTER_2] * len(fastq2),

        # Todo: what's the difference between ID & SM?
        # Todo: do we want the whole filename for ID? (see BWA IMPACT logs)
        # or abbreviate it (might be the way they do it in Roslin)
        'add_rg_ID': title_file[SAMPLE_ID_COLUMN].tolist(),
        'add_rg_SM': title_file[SAMPLE_ID_COLUMN].tolist(),
        'add_rg_LB': title_file[MANIFEST__LANE_COLUMN].tolist(),

        # Todo: should we use one or two barcodes in the PU field if they are different?
        'add_rg_PU': title_file[MANIFEST__BARCODE_ID_COLUMN].tolist(),

        # Patient ID needs to be a string, in case it is currently an integer
        'patient_id': [str(p) for p in title_file[MANIFEST__CMO_PATIENT_ID_COLUMN].tolist()],
        'sample_class': title_file[MANIFEST__SAMPLE_CLASS_COLUMN].tolist()
    }

    # Trim whitespace
    for key in samples_info:
        samples_info[key] = [x.strip() if type(x) == str else x for x in samples_info[key]]

    fh.write(ruamel.yaml.dump(samples_info))


def perform_length_checks(fastq1, fastq2, sample_sheet, title_file):
    """
    Check whether the title file matches input fastqs

    :param fastq1: List[dict] where each dict is a ruamel file object with `class` and `path` keys,
            (`path` being the path to the read 1 fastq)
    :param fastq2: List[dict] where each dict is a ruamel file object with `class` and `path` keys,
            (`path` being the path to the read 2 fastq)
    :param sample_sheet: List[dict] where each dict is a ruamel file object with `class` and `path` keys,
            (`path` being the path to the sample sheet)
    :param title_file:
    """
    try:
        assert len(fastq1) == len(fastq2)
    except AssertionError as e:
        print(DELIMITER + 'Error: Different number of read 1 and read 2 fastqs: {}'.format(repr(e)))
        print('fastq1: {}'.format(len(fastq1)))
        print('fastq2: {}'.format(len(fastq2)))
    try:
        assert len(sample_sheet) == len(fastq1)
    except AssertionError as e:
        print(DELIMITER + 'Error: Different number of sample sheet files & read 1 fastqs: {}'.format(repr(e)))
        print('fastq1: {}'.format(len(fastq1)))
        print('sample_sheets: {}'.format(len(sample_sheet)))
    try:
        assert title_file.shape[0] == len(fastq1)
    except AssertionError as e:
        print(DELIMITER + 'Error: Different number of fastqs files and samples in title file: {}'.format(repr(e)))
        print('fastq1: {}'.format(len(fastq1)))
        print('title file length: {}'.format(title_file.shape[0]))


def write_inputs_file(args, title_file, output_file_name):
    """
    Main function to write our inputs.yaml file.
    Contains most of the logic related to which inputs to use based on the type of run

    :param args:
    :param title_file:
    :param output_file_name:
    """
    tool_resources_file_path = TOOL_RESOURCES_LUNA

    if args.test:
        run_params_path = RUN_PARAMS_TEST
        run_files_path = RUN_FILES_TEST
    else:
        run_params_path = RUN_PARAMS
        run_files_path = RUN_FILES

    # Actually start writing the inputs file
    fh = open(output_file_name, 'wb')

    include_fastqs_params(fh, args.data_dir, title_file, args.title_file_path, args.force)
    include_yaml_resources(fh, run_params_path)
    include_yaml_resources(fh, run_files_path)
    include_yaml_resources(fh, tool_resources_file_path)

    fh.write(INPUTS_FILE_DELIMITER)
    # Include title_file in inputs.yaml
    title_file_obj = {'title_file': {'class': 'File', 'path': os.path.abspath(args.title_file_path)}}
    fh.write(ruamel.yaml.dump(title_file_obj))
    # This file itself is an input to the pipeline,
    # to include version details in the QC PDF
    inputs_yaml_object = {'inputs_yaml': {'class': 'File', 'path': os.path.abspath(output_file_name)}}
    fh.write(ruamel.yaml.dump(inputs_yaml_object))
    # Write the current project name for this run
    fh.write('project_name: {}'.format(args.project_name))
    # Write the current pipeline version for this pipeline
    include_version_info(fh)

    fh.close()


def check_final_file(output_file_name):
    """
    Check that lengths of these fields in the final file are equal:
    """
    with open(output_file_name, 'r') as stream:
        final_file = ruamel.yaml.round_trip_load(stream)

    # Todo: Use CONSTANTS
    fields_per_sample = [
        'add_rg_ID',
        'add_rg_LB',
        'add_rg_PU',
        'add_rg_SM',
        'patient_id',
        'fastq1',
        'fastq2',
        'sample_sheet',
        'adapter',
        'adapter2',
    ]

    try:
        for field in fields_per_sample:
            assert len(final_file[field]) == len(final_file['fastq1'])
    except AssertionError:
        print(DELIMITER + 'It looks like there aren\'t enough entries for one of these fields: {}'
              .format(fields_per_sample))
        print('Most likely, one of the samples is missing a read 1 fastq, read 2 fastq and/or sample sheet')


def parse_arguments():
    parser = argparse.ArgumentParser()

    # Required Arguments
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
        "-p",
        "--project_name",
        help="A name that describes the current data being run",
        required=True
    )

    # Optional Arguments
    parser.add_argument(
        "-t",
        "--test",
        help="Whether to run with test params or production params",
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-o",
        "--output_file_name",
        help="Name of yaml file for pipeline",
        required=True
    )
    parser.add_argument(
        "-f",
        "--force",
        help="Skip validation",
        required=False,
        action="store_true"
    )
    return parser.parse_args()


def perform_validation(title_file, title_file_path, project_name):
    """
    Make sure that we don't have any unacceptable entries in the title file:

    1. Sample IDs / Collab IDs must be unique
    2. Barcodes must be unique within each lane
    3. Sample_type is in ['Plasma', 'Buffy Coat']
    4. Sample Class is in ['Tumor', 'Normal']
    """
    if not project_name in title_file_path:
        print('WARNING: project ID not found in title file path. Are you sure you are using the correct title file?')

    if np.sum(title_file[SAMPLE_ID_COLUMN].duplicated()) > 0:
        raise Exception(DELIMITER + 'Duplicate sample IDs. Exiting.')

    if np.sum(title_file[MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN].duplicated()) > 0:
        raise Exception(DELIMITER + 'Duplicate investigator sample IDs. Exiting.')

    for lane in title_file[MANIFEST__LANE_COLUMN].unique():
        lane_subset = title_file[title_file[MANIFEST__LANE_COLUMN] == lane]

        if np.sum(lane_subset[MANIFEST__BARCODE_ID_COLUMN].duplicated()) > 0:
            raise Exception(DELIMITER + 'Duplicate barcode IDs in lane {}. Exiting.'.format(lane))

    if np.sum(title_file[MANIFEST__SAMPLE_CLASS_COLUMN].isin(['Tumor', 'Normal'])) < len(title_file):
        raise Exception(DELIMITER + 'Not all sample classes are in [Tumor, Normal]')

    if np.sum(title_file[MANIFEST__SAMPLE_TYPE_COLUMN].isin(['Plasma', 'Buffy Coat'])) < len(title_file):
        raise Exception(DELIMITER + 'Not all sample types are in [Plasma, Buffy Coat]')

    if not np.issubdtype(title_file[MANIFEST__LANE_COLUMN], np.number):
        raise Exception(DELIMITER + 'Lane column of title file must be integers')

    if title_file[MANIFEST__LANE_COLUMN].isnull().any():
        raise Exception(DELIMITER + 'Lane column of title file must not be missing or NA')


def print_user_message():
    print(DELIMITER)
    print('You\'ve just created the inputs file. Please double check its entries before kicking off a run.')
    print('Common mistakes include:')
    print('1. Trying to use test parameters on a real run (accidentally using the -t param)')
    print('2. Using the wrong bedfile for the capture')
    print('3. Working in the wrong virtual environment (are you sure you ran setup.py install?)')
    print('4. Not specifying the correct parameters for logLevel or cleanWorkDir ' +
          '(if you want to see the actual commands passed to the tools, or keep the temp outputs after a successful run)')
    print('5. Did you source the workspace_init.sh script (to make sure the PATH variable is set correctly?)')
    print('6. The "Sex" column of the title file will only correctly idenfity patients with [Male, M, Female, F] entries (although other entries will still be accepted).')


########
# Main #
########

def main():
    # Parse arguments
    args = parse_arguments()

    # Read title file
    title_file = pd.read_csv(args.title_file_path, sep='\t')

    # Sort based on Patient ID
    # This is done to ensure that the order of the samples is retained after indel realignment,
    # which groups the samples on a per-patient basis
    # Todo: This requirement / rule needs to be explicitly documented
    title_file = title_file.sort_values(SAMPLE_ID_COLUMN).reset_index(drop=True)

    # Perform some sanity checks on the title file
    if not args.force:
        perform_validation(title_file, args.title_file_path, args.project_name)
    # Create the inputs file for the run
    write_inputs_file(args, title_file, args.output_file_name)
    # Perform some checks on the final yaml file that will be supplied to the pipeline
    check_final_file(args.output_file_name)
    print_user_message()


if __name__ == '__main__':
    main()
