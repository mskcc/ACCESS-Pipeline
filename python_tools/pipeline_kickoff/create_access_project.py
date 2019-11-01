import os
import re
import argparse

##
# Create a directory structure for ACCESS Production Runs
#
# Usage: create_access_project -p Project_10151_B -o /home/user/my_run
#
# Results in:
#
# /output_location/project_id
#   /bam_qc
#   /structural_variants
#   /small_variants
#   /copy_number_variants
#   /microsatellite_instability


def project_id_regex(s, pat=re.compile(r"Project_\d{5}_.{1,2}")):
    """
    Validate Project ID (e.g. Project_10151_B)

    :param s: string
    :param pat: pattern to match
    :return: string
    """
    if not pat.match(s):
        print('Error: Project ID must match format "Project_10151_B"')
        raise argparse.ArgumentTypeError
    return s


def parse_arguments():
    """
    Parse args for project creation

    :return:
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-p",
        "--project_id",
        action="store",
        dest="project_id",
        type=project_id_regex,
        help="Project ID (e.g. Project_10151_B)",
        required=True,
    )

    parser.add_argument(
        "-o",
        "--output_location",
        action="store",
        dest="output_location",
        help="Directory to create project in",
        required=True,
    )

    return parser.parse_args()


def create_project_structure(args):
    """
    Create directories for the given project ID

    :return:
    """
    project_folder = os.path.join(args.output_location, args.project_id)

    bam_qc                          = os.path.join(project_folder, 'bam_qc')
    structural_variants             = os.path.join(project_folder, 'structural_variants')
    small_variants                  = os.path.join(project_folder, 'small_variants')
    copy_number_variants            = os.path.join(project_folder, 'copy_number_variants')
    microsatellite_instability      = os.path.join(project_folder, 'microsatellite_instability')

    os.mkdir(project_folder)
    os.mkdir(bam_qc)
    os.mkdir(structural_variants)
    os.mkdir(small_variants)
    os.mkdir(copy_number_variants)
    os.mkdir(microsatellite_instability)


def main():
    """

    :return:
    """
    args = parse_arguments()

    create_project_structure(args)
