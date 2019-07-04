import os
import sys
import csv
import glob
import ast
import logging
import argparse
import ruamel.yaml
from collections import defaultdict

from ..util import (
    include_yaml_resources,
    include_version_info
)

from ..constants import (
    ACCESS_MSI_RUN_FILES_PATH,
    ACCESS_MSI_RUN_PARAMS_PATH
)

##########
# Pipeline Inputs generation for the ACCESS Copy Number Variant Calling
#
# Usage:
# generate_msi_inputs -sb /dmp/analysis/prod/ACCESS/dms-qc/2019/ACCESSv1-VAL-20190010/access_qc-0.0.34-221-g3e7f923/standard_bams/ -o python_tools/pipeline_kickoff/inputs.yaml -od /dmp/hot/huy1 -p ACCESSv1-VAL-20190010 -alone

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.DEBUG)
logger = logging.getLogger('msi_pipeline_kickoff')


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
        '-p',
        '--project_name',
        help='project name',
        required=False
    )

    parser.add_argument(
        '-alone',
        '--stand_alone',
        help='Whether to run CNV as independent module',
        nargs='?',
        default=False,
        const=True,
        required=False
    )

    parser.add_argument(
        '-sb',
        '--standard_bams_directory',
        help='Directory that contains all standard bams to be used in MSI',
        required=True
    )

    parser.add_argument(
        '-od',
        '--output_directory',
        help='Output Directory for MSI Caller',
        required=True
    )

    args = parser.parse_args()
    return args


def get_bam_dics(args):
    """
    Retrieve bam list from given standard bam directory
    """
    tumorBamDic = {}
    normalBamDic = {}
    controlBamDic = {}
    for bam in glob.glob(os.path.join(args.standard_bams_directory, '*.bam')):
        sampleId = os.path.basename(bam).split('_')[0]
        if sampleId.startswith("SeraCare"):
            controlBamDic[sampleId] = bam
        elif sampleId.split('-')[-1].startswith('T'):
            tumorBamDic[sampleId] = bam
        elif sampleId.split('-')[-1].startswith('N'):
            normalBamDic['-'.join(sampleId.split('-')[:-1])] = bam

    return (tumorBamDic, normalBamDic, controlBamDic)


def create_inputs_file(args):
    """
    Create the inputs.yaml file for the ACCESS MSI

    :param args: argparse.ArgumentParser object
    """
    validate_args(args)

    (tumorBamDic, normalBamDic, controlBamDic) = get_bam_dics(args)
    if not tumorBamDic:
        raise Exception('Unable to get bam dics')

    path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    module = 'cwl_tools/msi'
    if not args.project_name:
        projName = ""
    else:
        projName = args.project_name

    # Generate bam lists
    fileTemp = '{"class": "File", "path": "%s"}'
    inputYamlFileList = defaultdict(list)
    for sampleId in tumorBamDic:
        patientId = '-'.join(sampleId.split('-')[:-1])
        # Include ONLY paired samples
        if patientId in normalBamDic:
            inputYamlFileList["sample_name"].append(sampleId)
            inputYamlFileList["tumor_bam"].append(ast.literal_eval(fileTemp % tumorBamDic[sampleId]))
            inputYamlFileList["normal_bam"].append(ast.literal_eval(fileTemp % normalBamDic[patientId]))

    inputYamlString = {
        "project_name_msi": projName,
        "file_path": os.path.join(path, module)
        #"msisensor_allele_counts": '{class: Directory, path: %s}' % args.output_directory
    }

    with open(args.output_file_name, 'w') as fh:
        fh.write("#### Inputs for MSI ####\n\n")
        for item in inputYamlString:
            fh.write("{}: {}\n".format(item, inputYamlString[item]))
        fh.write('\n# File and Directory Inputs\n')

        for item in inputYamlFileList:
            fh.write(ruamel.yaml.dump({item: inputYamlFileList[item]}))
            fh.write("\n")

        map(include_yaml_resources, [fh]*2,
            [ACCESS_MSI_RUN_FILES_PATH,
                ACCESS_MSI_RUN_PARAMS_PATH])

        if args.stand_alone:
            fh.write("tmp_dir: /dmp/analysis/SCRATCH\n")
            include_version_info(fh)

        fh.write("#### The end of for MSI ####\n")

    return True


def validate_args(args):
    """Arguments sanity check"""

    # Tumor bams folder is required for generating manifest list
    if not args.standard_bams_directory:
        raise Exception('--standard_bams_directory is required for MSI caller')

    if not args.output_file_name:
        raise Exception('--output_file_name is required for MSI caller')

    if not args.output_directory:
        raise Exception('--output_directory is required for MSI caller')

def main():
    """ Main """
    args = parse_arguments()
    create_inputs_file(args)
    return


if __name__ == '__main__':
    main()
