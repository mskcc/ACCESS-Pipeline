import os
import argparse
import ruamel.yaml

from python_tools.models import TitleFile
from python_tools.constants import (
    RUN_PARAMS__STANDARD_BAM_TO_COLLAPSED_QC
)
from python_tools.util import (
    get_pos,
    include_version_info,
    include_yaml_resources,
    find_bams_in_directory,
    create_yaml_file_objects
)


def read_title_file(title_file_path):
    """
    Instantiate and return title_file object

    :param title_file_path:
    :return:
    """
    return TitleFile(title_file_path)


def write_sample_info(fh, title_file):
    """
    Include the fields necessary for running the standard_bam_to_collapsed_qc workflow in the inputs file

    :param title_file:
    :return:
    """
    samples_info = {
        'add_rg_ID': title_file.get_cmo_sample_ids(),
        'add_rg_SM': title_file.get_cmo_sample_ids(),
        'add_rg_LB': title_file.get_lanes(),
        'add_rg_PU': title_file.get_barcode_ids(),
        'patient_id': title_file.get_patient_ids()
    }

    # Trim whitespace
    for key in samples_info:
        samples_info[key] = [x.strip() if type(x) == str else x for x in samples_info[key]]

    fh.write(ruamel.yaml.dump(samples_info))


def write_bams(fh, title_file, standard_bams_directory):
    """
    Include the paths to standard _MD_IR_FX_BR bams in our inputs file.

    Makes sure bams are in sorted order according to title file ordering

    :param standard_bams_directory:
    :return:
    """
    bams = find_bams_in_directory(standard_bams_directory)
    bams = create_yaml_file_objects(bams)
    bams = sorted(bams, key=lambda b: get_pos(title_file, b, True))
    fh.write(ruamel.yaml.round_trip_dump({'standard_bams': bams}))


def write_inputs_yaml(args):
    """
    Create the inputs.yaml file:

    1. Read title file
    2. Include sample fields
    3. Include standard bams paths
    4. Include params & file resources

    :param fh:
    :param output_file_name: Name to give to output file
    :return:
    """
    fh = open(args.output_file_name, 'wb')
    title_file = read_title_file(args.title_file_path)

    # Todo: need to refactor Util and other kickoff scripts to all use new TitleFile class
    write_bams(fh, title_file.__title_file__, args.standard_bams_directory)
    write_sample_info(fh, title_file)
    include_yaml_resources(fh, RUN_PARAMS__STANDARD_BAM_TO_COLLAPSED_QC)

    title_file_obj = {'title_file': {'class': 'File', 'path': args.title_file_path}}
    fh.write(ruamel.yaml.dump(title_file_obj))
    inputs_yaml_object = {'inputs_yaml': {'class': 'File', 'path': os.path.abspath(args.output_file_name)}}
    fh.write(ruamel.yaml.dump(inputs_yaml_object))
    fh.write('project_name: {}'.format(args.project_name))
    include_version_info(fh)

    fh.close()


def parse_arguments():
    """
    Standard Argparser method

    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--title_file_path",
        help="Title File with all necessary columns and information",
        required=True
    )
    parser.add_argument(
        "-b",
        "--standard_bams_directory",
        help="Directory with standard bams (will be searched recursively)",
        required=True
    )
    parser.add_argument(
        "-p",
        "--project_name",
        help="A name that describes the current data being run",
        required=True
    )
    parser.add_argument(
        "-o",
        "--output_file_name",
        help="Name of yaml file for pipeline",
        required=True
    )
    return parser.parse_args()


def main():
    """
    Main
    """
    args = parse_arguments()
    write_inputs_yaml(args)


if __name__ == '__main__':
    main()
