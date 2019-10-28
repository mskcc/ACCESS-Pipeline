"""
Script to create the folder structure specific for ACCESS projects.

Will result in the following structure:

/study_ID
    /small_variants
    /structural_variants
    /copy_number_variants
    /microsatellite_instability
    /bam_qc

Wich correspond to results from the following pipelines:

snps_and_indels.cwl
manta.cwl
cnv.cwl
msi.cwl
ACCESS_Pipeline.cwl
"""

import os
import re
import argparse

ACCESS_RUNS_FOLDER = '/work/production/runs'

RESULTS_FOLDERS = [
    'copy_number_variants',
    'small_variants',
    'structural_variants',
    'microsatellite_instability',
    'bam_qc'
]


def pipeline_version_validation(s, pat=re.compile(r"\d{5}-[A-Z]{1,3}")):
    """
    Util for parsing version number for argparse argument

    Example project ID:

    05500-FN
    """
    if not pat.match(s):
        raise argparse.ArgumentTypeError
    return s


def project_id_validation(s, pat=re.compile(r"\d{1}\.\d{1,2}\.\d{1,3}")):
    """
    Util for parsing version number for argparse argument

    Example pipeline version:

    1.3.12
    """
    if not pat.match(s):
        raise argparse.ArgumentTypeError
    return s


def main():
    """
    Parse arguments and create folder structure
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-p',
        '--project_id',
        help='Project ID (e.g. 05500-FN) (Required)',
        required=True,
        type=project_id_validation
    )

    parser.add_argument(
        '-v',
        '--pipeline_version',
        help='Pipeline version', # Todo: can validate from git --tags?
        required=True,
        type=pipeline_version_validation
    )

    args = parser.parse_args()

    project_parts = [ACCESS_RUNS_FOLDER, args.project_id, args.pipeline_version]
    os.mkdir(os.path.join(project_parts))

    for folder in RESULTS_FOLDERS:
        os.mkdir(os.path.join(project_parts, folder))


if __name__ == '__main__':
    main()
