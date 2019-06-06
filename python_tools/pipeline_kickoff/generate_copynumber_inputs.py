import os
import sys
import csv
import glob
import logging
import argparse
import ruamel.yaml

from ..util import (
    include_yaml_resources,
    include_version_info
)

from ..constants import (
    ACCESS_COPYNUMBER_RUN_FILES_PATH,
    ACCESS_COPYNUMBER_RUN_PARAMS_PATH
)

##########
# Pipeline Inputs generation for the ACCESS-Variants pipeline
#
# Todo:
# - better way to ensure proper sort order of samples
# - combine this with create_ scripts
# - singularity
#
# Usage:
#
# generate_access_variants_inputs \
# -pn \
# Variant_Calling_Project \
# -o \
# inputs.yaml \
# -dn /home/patelju1/projects/Juber/HiSeq/5500-FF-new/run-5500-FF/FinalBams/DA-ret-004-pl-T01-IGO-05500-FF-18_bc427_Pool-05500-FF-Tube3-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR.bam \
# -p \
# ./test_pairs.tsv \
# -tb \
# ~/PROJECT_tumor_bams/duplex_bams \
# -nb \
# ~/PROJECT_normal_bams/duplex_bams \
# -sb \
# ~/PROJECT_normal_bams/simplex_bams \
# -cbd \
# ~/ACCESSv1-VAL-20180003_curated_bams \
# -cbs \
# ~/ACCESSv1-VAL-20180003_curated_bams_simplex
# -m

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.DEBUG)
logger = logging.getLogger('copy_number_pipeline_kickoff')


def parse_arguments():
    """
    Parse arguments for copy number calling pipeline inputs generation

    :return: argparse.ArgumentParser object
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-o',
        '--output_file_name',
        help='Filename for yaml file to be used as pipeline inputs',
        required=True
    )

    parser.add_argument(
        '-pn',
        '--project_name',
        help='Project name for this run',
        required=False #should this be True?
    )

    parser.add_argument(
        '-t',
        '--title_file_path',
        help='title file in tsv format',
        required=True
    )

    parser.add_argument(
        '-tb',
        '--tumor_bams_directory',
        help='Directory that contains all unfiltered tumor bams to be used in copy number variant calling',
        required=True
    )

    parser.add_argument(
        '-e',
        '--engine_type',
        help='Type of engine the job will be submitting',
        required=True
    )

    parser.add_argument(
        '-q',
        '--queue',
        help='Queue used for job submitting',
        required=True
    )

    parser.add_argument(
        '-od',
        '--output_directory',
        help='Output Directory for copy number variant calling',
        required=True
    )

    args = parser.parse_args()
    return args


def get_sampleID_and_sex(args):
    """
    Retrieve sample IDs (samples with "-T*") and patient sex from title file
    """

    sample2sex = {}
    projName = ""
    with open(args.title_file_path, 'rU') as titleFile:
        tfDict = csv.DictReader(titleFile, delimiter='\t')
        for row in tfDict:
            if row["Sample"].split('-')[1].startswith('T'):
                sex = row["Sex"].replace("F", "Female").replace("M", "Male")
                sample2sex[row["Sample"]] = sex
                projName = row["Pool"]
    return (sample2sex, projName)


def get_bam_list(args):
    """
    Retrieve bam list from given tumor bam directory
    """
    bamList = []
    for bam in glob.glob(os.path.join(args.tumor_bams_directory, '*.bam')):
        if os.path.basename(bam).split('-')[1].startswith('T'):
            bamList.append(bam)
    return bamList


def generate_manifest_file(args, sample2sex, bamList):
    """
    Generate tumor manifest file with patient sex
    """
    fileName = os.path.join(args.output_directory, "tumor_manifest.txt")
    output = ""
    for bam in bamList:
        sampleId = os.path.basename(bam).split('_')[0]
        sex = sample2sex[sampleId]
        output += bam + "\t" + sex + "\n"

    with open(fileName, 'w') as maniFile:
        maniFile.write(output)

    return fileName


def create_inputs_file(args):
    """
    Create the inputs.yaml file for the ACCESS Copy Number Variant Calling pipeline

    :param args: argparse.ArgumentParser object
    """
    validate_args(args)

    (sample2sex, projName) = get_sampleID_and_sex(args)
    bamList = get_bam_list(args)
    if not sample2sex or not bamList:
        raise Exception('Unable to load title file or get bam list')

    inputYamlString = {
        "tumor_sample_list": generate_manifest_file(args, sample2sex, bamList),
        "project_name": projName,
        "r_path": "R",
        "queue": args.queue
    }

    if args.engine_type.find('qsub') != -1:
        inputYamlString["qsub"] = args.engine_type
    else:
        inputYamlString["bsub"] = args.engine_type

    inputYamlOther = {
        "loess_normalize_script": {"class": "File", "path": "/dmp/hot/ptashkir/cfdna_scna/ACCESS_CNV/scripts/loessnormalize_nomapq_cfdna.R"},
        "copy_number_script": {"class": "File", "path": "/dmp/hot/ptashkir/cfdna_scna/ACCESS_CNV/scripts/copynumber_tm.batchdiff_cfdna.R"},
        "output": {"class": "Directory", "path": args.output_directory}
    }

    with open(args.output_file_name, 'w') as fh:
        for item in inputYamlString:
            fh.write("{}: {}\n".format(item, inputYamlString[item]))
        fh.write('\n\n# File and Directory Inputs\n')
        fh.write(ruamel.yaml.dump(inputYamlOther))

        map(include_yaml_resources, [fh]*2,
            [ACCESS_COPYNUMBER_RUN_FILES_PATH,
                ACCESS_COPYNUMBER_RUN_PARAMS_PATH])

        include_version_info(fh)

    return True


def validate_args(args):
    """Arguments sanity check"""

    # Either one of title file or pairing file is required for this process
    if not args.title_file_path:
        raise Exception('--title_file_path is required to determine tumor samples for copy number variant calling.')

    # Tumor bams folder is required for generating manifest list
    if not args.tumor_bams_directory:
        raise Exception('--tumor_bams_directory is required for copy number variant calling.')

    if not args.output_directory:
        raise Exception('--output_directory is required for copy number variant calling')

    if not args.output_file_name:
        raise Exception('--output_file_name is required for copy number variant calling')

    if not args.engine_type:
        raise Exception('--engine_type is required for copy number variant calling')

    if not args.queue:
        raise Exception('--queue is required for copy number variant calling')


def main():
    """ Main """
    args = parse_arguments()
    create_inputs_file(args)
    return


if __name__ == '__main__':
    main()
