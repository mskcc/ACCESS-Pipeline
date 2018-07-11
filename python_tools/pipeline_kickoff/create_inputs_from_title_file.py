import sys
import argparse
import ruamel.yaml
import numpy as np
import pandas as pd

# Paths to the default run arguments for testing or runs
from ..constants import *


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
# Some input parameters may take on multiple values based on what system we are running on (e.g. compute cluster or Local)
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


# Static adapter sequences that surround the barcodes
# Used by the Trimgalore step in the pipeline
#
# See notes/adapters for full descriptions across all cases
ADAPTER_1_PART_1 = 'AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC'
ADAPTER_1_PART_2 = 'ATCTCGTATGCCGTCTTCTGCTTG'
ADAPTER_2_PART_1 = 'AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT'
ADAPTER_2_PART_2 = 'AGATCTCGGTGGTCGCCGTATCATT'

# Template identifier string that will get replaced with the project root location
PIPELINE_ROOT_PLACEHOLDER = '$PIPELINE_ROOT'

# Strings to target when looking for Illumina run files
FASTQ_1_FILE_SEARCH = '_R1_001.fastq.gz'
FASTQ_2_FILE_SEARCH = '_R2_001.fastq.gz'
SAMPLE_SHEET_FILE_SEARCH = 'SampleSheet.csv'

# Delimiter for printing logs
DELIMITER = '\n' + '*' * 20 + '\n'
# Delimiter for inputs file sections
INPUTS_FILE_DELIMITER = '\n\n' + '# ' + '--' * 30 + '\n\n'


def load_fastqs(data_dir):
    """
    Recursively find files in `data_dir` with the given `file_regex`

    Todo: need to support multiple R1 / R2 fastqs per patient?
    Or maybe not b/c "The last segment is always 001":
    https://support.illumina.com/content/dam/illumina-support/documents/documentation/software_documentation/bcl2fastq/bcl2fastq2_guide_15051736_v2.pdf
    Page 19

    Note:
    os.walk yields a 3-list (dirpath, dirnames, filenames)
    """
    # Gather Sample Sub-directories (but leave out the parent dir)
    folders = list(os.walk(data_dir))

    # Filter to those that contain a read 1, read 2, and sample sheet
    folders_2 = filter(lambda folder: any([FASTQ_1_FILE_SEARCH in x for x in folder[2]]), folders)
    folders_3 = filter(lambda folder: any([FASTQ_2_FILE_SEARCH in x for x in folder[2]]), folders_2)
    folders_4 = filter(lambda folder: any([SAMPLE_SHEET_FILE_SEARCH in x for x in folder[2]]), folders_3)

    # Issue a warning
    if not len(folders) == len(folders_4):
        # Todo: Inform user which samples might be missing
        print(DELIMITER + 'Warning, some samples may not have a Read 1, Read 2, or sample sheet. Please manually check inputs.yaml')

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


def get_adapter_sequences(title_file):
    """
    Adapter sequences need to be tailored to include each sample barcode from the title file

    p7_end - bc_1 - primer_binding_site_7

    primer_binding_site_5 - bc_2 - p5_end

    These will be used during the Trimgalore adapter trimming step
    :param title_file:
    :return:
    """
    # First, check that there are no duplicate barcodes
    perform_duplicate_barcodes_check(title_file)

    barcodes_one = title_file[TITLE_FILE__BARCODE_INDEX_1_COLUMN]
    barcodes_two = title_file[TITLE_FILE__BARCODE_INDEX_2_COLUMN]

    adapter = ADAPTER_1_PART_1
    adapter += barcodes_one
    adapter += ADAPTER_1_PART_2

    adapter2 = ADAPTER_2_PART_1
    adapter2 += barcodes_two
    adapter2 += ADAPTER_2_PART_2

    return adapter, adapter2


def perform_duplicate_barcodes_check(title_file):
    """
    Check that no two samples IN THE SAME LANE have the same barcode 1 or barcode 2
    """
    for lane in title_file[TITLE_FILE__LANE_COLUMN].unique():
        lane_subset = title_file[title_file[TITLE_FILE__LANE_COLUMN] == lane]

        if np.sum(title_file[TITLE_FILE__BARCODE_INDEX_1_COLUMN].duplicated()) > 0:
            raise Exception(DELIMITER + 'Duplicate barcodes for barcode 1, lane {}. Exiting.'.format(lane))

        if np.sum(title_file[TITLE_FILE__BARCODE_INDEX_2_COLUMN].duplicated()) > 0:
            raise Exception(DELIMITER + 'Duplicate barcodes for barcode 2, lane {}. Exiting.'.format(lane))


def contained_in(sample_id, fastq_object):
    """
    Helper method to sort list of fastqs.
    Returns True if `value` contained in `string`, False otherwise
    """
    found = sample_id.replace('_', '-') in fastq_object['path'].replace('_', '-')
    if found:
        return 1
    else:
        return 0


def get_pos(title_file, fastq_object):
    """
    Return position of `fastq_object` in 'Sample_ID' column of title_file
    Used for sorting purposes
    """
    boolv = title_file[TITLE_FILE__SAMPLE_ID_COLUMN].apply(contained_in, fastq_object=fastq_object)

    if np.sum(boolv) > 1:
        raise Exception('More than one fastq found for patient, exiting.')

    # If there are no matches, throw error
    if np.sum(boolv) < 1:
        err_string = DELIMITER + 'Error, matching sample ID for file {} not found in title file'
        print >> sys.stderr, err_string.format(fastq_object)
        raise Exception('Please double check the order of the fastqs in the final inputs.yaml file')

    pos = np.argmax(boolv)
    return pos


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
    found_boolv = np.array([any([sample in f['path'] for f in fastq1]) for sample in title_file[TITLE_FILE__SAMPLE_ID_COLUMN]])
    samples_not_found = title_file.loc[~found_boolv, TITLE_FILE__SAMPLE_ID_COLUMN]

    if samples_not_found.shape[0] > 0:
        print(DELIMITER + 'Error: The following samples were missing either a read 1 fastq, read 2 fastq, or sample sheet. ' +
                          'These samples will be removed from the title file so that the remaining samples can be run.')
        print('Please perform a manual check on the inputs file before running the pipeline.')
        print(samples_not_found)

    title_file = title_file.loc[found_boolv, :]
    title_file.to_csv(title_file_path, sep='\t', index=False)
    return title_file


def remove_missing_fastq_samples(fastq1, fastq2, sample_sheet, title_file):
    """
    Todo: For the SampleSheet files, this relies on the parent folder containing the sample name
    """
    fastq1 = filter(lambda f: any([sid in f['path'] for sid in title_file[TITLE_FILE__SAMPLE_ID_COLUMN]]), fastq1)
    fastq2 = filter(lambda f: any([sid in f['path'] for sid in title_file[TITLE_FILE__SAMPLE_ID_COLUMN]]), fastq2)
    sample_sheet = filter(lambda s: any([sid in s['path'] for sid in title_file[TITLE_FILE__SAMPLE_ID_COLUMN]]), sample_sheet)

    return fastq1, fastq2, sample_sheet


def perform_patient_id_checks(fastq1, fastq2, title_file):
    # Todo: Using correct title file column to match samples in data folder?
    for patient_id in title_file[TITLE_FILE__COLLAB_ID_COLUMN]:
        assert any([patient_id in f['path'] for f in fastq1]), 'Missing fastq1 for patient id: {}'.format(patient_id)
        assert any([patient_id in f['path'] for f in fastq2]), 'Missing fastq2 for patient id: {}'.format(patient_id)


def perform_barcode_index_checks(title_file, sample_sheets):
    """
    Confirm that the barcode indexes in the title file,
    match to what is listed in the Sample Sheet files from the Illumina Run

    :param title_file:
    :param sample_sheets:
    :return:
    """
    for sample_id in title_file[TITLE_FILE__SAMPLE_ID_COLUMN]:
        cur_sample = title_file[title_file[TITLE_FILE__SAMPLE_ID_COLUMN] == sample_id]

        matching_sample_sheets = [s for s in sample_sheets if sample_id in s.get('path')]
        assert len(matching_sample_sheets) == 1

        sample_sheet = matching_sample_sheets[0]
        sample_sheet_df = pd.read_csv(sample_sheet['path'], sep=',')

        assert sample_sheet_df['Index'].values[0] == cur_sample[TITLE_FILE__BARCODE_INDEX_1_COLUMN].values[0]
        assert sample_sheet_df['Index2'].values[0] == cur_sample[TITLE_FILE__BARCODE_INDEX_2_COLUMN].values[0]


def include_fastqs_params(fh, data_dir, title_file, title_file_path):
    """
    Write fastq1, fastq2, read group identifiers and sample_sheet file references to yaml inputs file.
    """
    # Load and sort our data files
    fastq1, fastq2, sample_sheets = load_fastqs(data_dir)
    # Get rid of data files that don't have an entry in the title_file
    fastq1, fastq2, sample_sheets = remove_missing_fastq_samples(fastq1, fastq2, sample_sheets, title_file)
    # Get rid of entries from title file that are missing data files
    title_file = remove_missing_samples_from_title_file(title_file, fastq1, title_file_path)
    # Sort everything based on the ordering in the title_file
    fastq1, fastq2, sample_sheets = sort_fastqs(fastq1, fastq2, sample_sheets, title_file)

    # Check that we have the same number of everything
    perform_length_checks(fastq1, fastq2, sample_sheets, title_file)

    # Check that patient ids are found in fastq filenames
    # That is how we pair Tumors and Normals
    perform_patient_id_checks(fastq1, fastq2, title_file)

    # Check the barcode sequences in the title_file against the sequences in the sample_sheets
    perform_barcode_index_checks(title_file, sample_sheets)

    # Build adapters from title_file (todo: build from sample sheet once dual indices are available?)
    adapter, adapter2 = get_adapter_sequences(title_file)

    out_dict = {
        'fastq1': fastq1,
        'fastq2': fastq2,
        'sample_sheet': sample_sheets,
        'adapter': adapter.tolist(),
        'adapter2': adapter2.tolist(),

        # Todo: what's the difference between ID & SM?
        # Todo: do we want the whole filename for ID? (see BWA IMPACT logs)
        # or abbreviate it (might be the way they do it in Roslin)
        'add_rg_ID': title_file[TITLE_FILE__SAMPLE_ID_COLUMN].tolist(),
        'add_rg_SM': title_file[TITLE_FILE__SAMPLE_ID_COLUMN].tolist(),
        'add_rg_LB': title_file[TITLE_FILE__LANE_COLUMN].tolist(),

        # Todo: should we use one or two barcodes in the PU field if they are different?
        'add_rg_PU': title_file[TITLE_FILE__BARCODE_ID_COLUMN].tolist(),
        'patient_id': title_file[TITLE_FILE__PATIENT_ID_COLUMN].tolist(),
        'class_list': title_file[TITLE_FILE__CLASS_COLUMN].tolist(),
    }

    # Trim whitespace
    for key in out_dict:
        out_dict[key] = [x.strip() if type(x) == str else x for x in out_dict[key]]

    fh.write(ruamel.yaml.dump(out_dict))


def substitute_project_root(yaml_file):
    """
    Substitute in the ROOT_PATH variable based on our current installation directory
    The purpose of this method is to support referencing resources in the resources folder
    This may be unnecessary now that we manually set the RESOURCES_ROOT variable in constants.py
    """
    for key in yaml_file.keys():
        # If we are dealing with a File object
        if 'path' in yaml_file[key]:
            new_value = yaml_file[key]['path'].replace(PIPELINE_ROOT_PLACEHOLDER, ROOT_DIR)
            yaml_file[key]['path'] = new_value

        # If we are dealing with a string
        # Todo: should be replaced with File
        if type(yaml_file[key]) == str:
            new_value = yaml_file[key].replace(PIPELINE_ROOT_PLACEHOLDER, ROOT_DIR)
            yaml_file[key] = new_value

    return yaml_file


def include_file_resources(fh, file_resources_path):
    """
    Write the paths to our resource files into the inputs yaml file.
    """
    with open(file_resources_path, 'r') as stream:
        file_resources = ruamel.yaml.round_trip_load(stream)

    file_resources = substitute_project_root(file_resources)
    fh.write(INPUTS_FILE_DELIMITER + ruamel.yaml.round_trip_dump(file_resources))


def include_run_params(fh, run_params_path):
    """
    Load and write our default run parameters
    """
    with open(run_params_path, 'r') as stream:
        other_params = ruamel.yaml.round_trip_load(stream)

    fh.write(INPUTS_FILE_DELIMITER + ruamel.yaml.round_trip_dump(other_params))


def include_resource_overrides(fh):
    """
    Load and write our ResourceRequirement overrides for testing

    :param fh: File handle for pipeline yaml inputs
    """
    with open(RESOURCE_OVERRIDES_FILE_PATH, 'r') as stream:
        resource_overrides = ruamel.yaml.round_trip_load(stream)

    fh.write(INPUTS_FILE_DELIMITER + ruamel.yaml.round_trip_dump(resource_overrides))


def include_tool_resources(fh, tool_resources_file_path):
    """
    Load and write our ResourceRequirement overrides for testing

    :param fh: File handle for pipeline yaml inputs
    """
    with open(tool_resources_file_path, 'r') as stream:
        tool_resources = ruamel.yaml.round_trip_load(stream)
        tool_resources = substitute_project_root(tool_resources)

    fh.write(INPUTS_FILE_DELIMITER + ruamel.yaml.round_trip_dump(tool_resources))


def perform_length_checks(fastq1, fastq2, sample_sheet, title_file):
    """
    Check whether the title file matches input fastqs

    Todo: we might want an option to remove fastqs or rows from the title_file instead of throwing error,
    in the event that we use this script on a subset of the fastqs in a pool
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


def include_collapsing_params(fh, test=False, local=False):
    """
    Load and write our Collapsing & QC parameters

    :param fh: File handle for pipeline yaml inputs
    :param test: Whether to include test or production collapsing params
    """
    if local:
        # Local run params are same as Test params
        collapsing_parameters = RUN_PARAMS_TEST_COLLAPSING
        collapsing_files = RUN_FILES_LOCAL_COLLAPSING
    elif test:
        collapsing_parameters = RUN_PARAMS_TEST_COLLAPSING
        collapsing_files = RUN_FILES_TEST_COLLAPSING
    else:
        collapsing_parameters = RUN_PARAMS_COLLAPSING
        collapsing_files = RUN_FILES_COLLAPSING

    with open(collapsing_parameters, 'r') as stream:
        collapsing_parameters = ruamel.yaml.round_trip_load(stream)

    fh.write(INPUTS_FILE_DELIMITER + ruamel.yaml.round_trip_dump(collapsing_parameters))

    with open(collapsing_files, 'r') as stream:
        file_resources = ruamel.yaml.round_trip_load(stream)

    file_resources = substitute_project_root(file_resources)

    fh.write(INPUTS_FILE_DELIMITER + ruamel.yaml.round_trip_dump(file_resources))


def write_inputs_file(args, title_file, output_file_name):
    """
    Main function to write our inputs.yaml file.
    Contains most of the logic related to which inputs to use based on the type of run
    """
    tool_resources_file_path = TOOL_RESOURCES_LUNA

    if args.local:
        # Local run params are same as Test params
        run_params_path = RUN_PARAMS_TEST
        run_files_path = RUN_FILES_LOCAL
        tool_resources_file_path = TOOL_RESOURCES_LOCAL
    elif args.test:
        run_params_path = RUN_PARAMS_TEST
        run_files_path = RUN_FILES_TEST
    else:
        run_params_path = RUN_PARAMS
        run_files_path = RUN_FILES

    # Actually start writing the inputs file
    fh = open(output_file_name, 'wb')

    include_fastqs_params(fh, args.data_dir, title_file, args.title_file_path)
    include_run_params(fh, run_params_path)
    include_file_resources(fh, run_files_path)
    include_tool_resources(fh, tool_resources_file_path)

    if args.collapsing:
        include_collapsing_params(fh, args.test, args.local)

    # Optionally override ResourceRequirements with smaller values when testing
    # if args.include_resource_overrides:
    #     include_resource_overrides(fh)

    # Include title_file in inputs.yaml
    title_file_obj = {'title_file': {'class': 'File', 'path': args.title_file_path}}
    fh.write(ruamel.yaml.dump(title_file_obj))

    # This file itself is an input to the pipeline,
    # to include version details in the QC PDF
    inputs_yaml_object = {'inputs_yaml': {'class': 'File', 'path': output_file_name}}
    fh.write(ruamel.yaml.dump(inputs_yaml_object))
    include_version_info(fh)

    fh.close()


def include_version_info(fh):
    """
    Todo: Include indentifier to indicate if commit == tag
    """
    import version
    fh.write(INPUTS_FILE_DELIMITER)
    fh.write('version: {} \n'.format(version.most_recent_tag))
    fh.write('# Pipeline Run Version Information: \n')
    fh.write('# Version: {} \n'.format(version.version))
    fh.write('# Short Version: {} \n'.format(version.short_version))
    fh.write('# Most Recent Tag: {} \n'.format(version.most_recent_tag))
    fh.write('# Dirty? {} \n'.format(str(version.dirty)))


def check_final_file(output_file_name):
    """
    Check that lengths of these fields in the final file are equal:
    """
    with open(output_file_name, 'r') as stream:
        final_file = ruamel.yaml.round_trip_load(stream)

    # Todo: Use CONSTANTS
    fields_per_sample = [
        'adapter',
        'adapter2',
        'add_rg_ID',
        'add_rg_LB',
        'add_rg_PU',
        'add_rg_SM',
        'class_list',
        'patient_id',
        'fastq1',
        'fastq2',
        'sample_sheet',
    ]

    try:
        for field in fields_per_sample:
            assert len(final_file[field]) == len(final_file['fastq1'])
    except AssertionError:
        print(DELIMITER + 'It looks like there aren\'t enough entries for one of these fields: {}'.format(fields_per_sample))
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

    # Optional Arguments
    parser.add_argument(
        "-t",
        "--test",
        help="Whether to run with test params or production params",
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-c",
        "--collapsing",
        help="Whether to only generate inputs necessary for standard bams, or to run full pipeline with collapsing.",
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-l",
        "--local",
        help="Whether to use paths to tool specified for local pipeline operation",
        required=False,
        action="store_true"
    )
    parser.add_argument(
        "-o",
        "--output_file_name",
        help="Name of yaml file for pipeline",
        required=True
    )
    return parser.parse_args()


def perform_validation(title_file):
    """
    Make sure that we don't have any unacceptable entries in the title file:

    1. Sample IDs must be unique
    2. Barcodes must be unique within each lane
    3. Sample_type is in ['Plasma', 'Buffy Coat']
    4. Sex is one of ['Male, 'M', 'Female', 'F']
    5. Sample Class is in ['Tumor', 'Normal']
    """
    if np.sum(title_file[TITLE_FILE__SAMPLE_ID_COLUMN].duplicated()) > 0:
        raise Exception(DELIMITER + 'Duplicate sample names. Exiting.')

    for lane in title_file[TITLE_FILE__LANE_COLUMN].unique():
        lane_subset = title_file[title_file[TITLE_FILE__LANE_COLUMN] == lane]

        if np.sum(lane_subset[TITLE_FILE__BARCODE_ID_COLUMN].duplicated()) > 0:
            raise Exception(DELIMITER + 'Duplicate barcode IDs. Exiting.')

    if np.sum(title_file[TITLE_FILE__CLASS_COLUMN].isin(['Tumor', 'Normal'])) < len(title_file):
        raise Exception(DELIMITER + 'Not all sample classes are in [Tumor, Normal]')

    if np.sum(title_file[TITLE_FILE__SAMPLE_TYPE_COLUMN].isin(['Plasma', 'Buffy Coat'])) < len(title_file):
        raise Exception(DELIMITER + 'Not all sample types are in [Plasma, Buffy Coat]')

    if np.sum(title_file[TITLE_FILE__SEX_COLUMN].isin(['Male', 'M', 'Female', 'F'])) < len(title_file):
        raise Exception(DELIMITER + 'Not all sex entries are in [Male, M, Female, F]')


def print_user_message():
    print(DELIMITER)
    print('You\'ve just created the inputs file. Please double check its entries before kicking off a run.')
    print('Common mistakes include:')
    print('1. Trying to use test parameters on a real run (accidentally using the -t param)')
    print('2. Using the wrong bedfile for the capture')
    print('3. Not specifying the \'-c\' parameter when collapsing steps are intended')
    print('4. Working in the wrong virtual environment (are you sure you ran setup.py install?)')
    print('5. Using the wrong adapter sequences (this setup only support dual-indexing)')
    print('6. Not specifying the correct parameters for logLevel or cleanWorkDir ' +
          '(if you want to see the actual commands passed to the tools, or keep the temp outputs after a successful run)')


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
    title_file = title_file.sort_values(TITLE_FILE__PATIENT_ID_COLUMN).reset_index(drop=True)

    # Perform some sanity checks on the title file
    perform_validation(title_file)
    # Create the inputs file for the run
    write_inputs_file(args, title_file, args.output_file_name)
    # Perform some checks on the final yaml file that will be supplied to the pipeline
    check_final_file(args.output_file_name)
    print_user_message()


if __name__ == '__main__':
    main()
