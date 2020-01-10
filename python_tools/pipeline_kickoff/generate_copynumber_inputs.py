import os
import sys
import csv
import glob
import logging
import argparse
import ruamel.yaml

from python_tools.util import include_yaml_resources, include_version_info

from python_tools.constants import (
    ACCESS_COPYNUMBER_RUN_FILES_PATH,
    ACCESS_COPYNUMBER_RUN_PARAMS_PATH,
    VERSION_PARAM,
)

##########
# Pipeline Inputs generation for the ACCESS Copy Number Variant Calling
#
# Usage:
# generate_copynumber_inputs -t /dmp/analysis/prod/ACCESS/dms-qc/2019/ACCESSv1-VAL-20190010/title_file.txt -tb /dmp/analysis/prod/ACCESS/dms-qc/2019/ACCESSv1-VAL-20190010/access_qc-0.0.34-221-g3e7f923/unfiltered_bams/ -o python_tools/pipeline_kickoff/inputs.yaml -od /dmp/hot/huy1 -alone

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)
logger = logging.getLogger("copy_number_pipeline_kickoff")


def parse_arguments():
    """
    Parse arguments for copy number calling pipeline inputs generation

    :return: argparse.ArgumentParser object
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-o",
        "--output_file_name",
        help="Filename for yaml file to be used as pipeline inputs",
        required=True,
    )

    parser.add_argument(
        "-alone",
        "--stand_alone",
        help="Whether to run CNV as independent module",
        nargs="?",
        default=False,
        const=True,
        required=False,
    )

    parser.add_argument(
        "-t", "--title_file_path", help="title file in tsv format", required=True
    )

    parser.add_argument(
        "-tb",
        "--tumor_bams_directory",
        help="Directory that contains all unfiltered tumor bams to be used in copy number variant calling",
        required=True,
    )

    parser.add_argument(
        "-e",
        "--engine_type",
        help="Type of engine the job will be submitting",
        required=False,
    )

    parser.add_argument(
        "-q", "--queue", help="Queue used for job submitting", required=False
    )

    parser.add_argument(
        "-od",
        "--output_directory",
        help="Output Directory for copy number variant calling",
        required=True,
    )

    args = parser.parse_args()
    return args


def get_sampleID_and_sex(args):
    """
    Retrieve sample IDs (samples with "-T*") and patient sex from title file
    """

    sample2sex = {}
    projName = ""
    with open(args.title_file_path, "rU") as titleFile:
        tfDict = csv.DictReader(titleFile, delimiter="\t")
        for row in tfDict:
            if row["Sample"].split("_")[0].split("-")[-1].startswith("T"):
                sex = row["Sex"].replace("Female", "Female").replace("Male", "Male")
                sample2sex[row["Sample"]] = sex
                projName = row["Pool"]
    return (sample2sex, projName)


def get_bam_list(args):
    """
    Retrieve bam list from given tumor bam directory
    """
    bamList = []
    for bam in glob.glob(os.path.join(args.tumor_bams_directory, "*.bam")):
        if os.path.basename(bam).split("_")[0].split("-")[-1].startswith("T"):
            bamList.append(bam)
    return bamList


def generate_manifest_file(args, sample2sex, bamList):
    """
    Generate tumor manifest file with patient sex
    """
    fileName = os.path.join(args.output_directory, "tumor_manifest.txt")
    output = ""
    for bam in bamList:
        sampleId = os.path.basename(bam).split("_")[0]
        if sampleId in sample2sex:
            sex = sample2sex[sampleId]
            output += bam + "\t" + sex + "\n"

    with open(fileName, "w") as maniFile:
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
        raise Exception("Unable to load title file or get bam list")

    path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    module = "cwl_tools/cnv"

    inputYamlString = {
        "project_name_cnv": projName,
        "file_path": os.path.join(path, module),
    }

    inputYamlOther = {
        "tumor_sample_list": {
            "class": "File",
            "path": generate_manifest_file(args, sample2sex, bamList),
        }
    }

    with open(args.output_file_name, "w") as fh:
        fh.write("#### Inputs for Copy Number Variant Calling ####\n\n")
        for item in inputYamlString:
            fh.write("{}: {}\n".format(item, inputYamlString[item]))
        fh.write("\n# File and Directory Inputs\n")
        fh.write(ruamel.yaml.dump(inputYamlOther))

        map(
            include_yaml_resources,
            [fh] * 2,
            [ACCESS_COPYNUMBER_RUN_FILES_PATH, ACCESS_COPYNUMBER_RUN_PARAMS_PATH],
        )

        if args.stand_alone:
            fh.write("tmp_dir: /dmp/analysis/SCRATCH\n")
            # Write the current pipeline version for this pipeline
            try:
                include_yaml_resources(fh, VERSION_PARAM)
            except IOError:
                # that is if version.yaml is absent
                fh.write(INPUTS_FILE_DELIMITER)
                fh.write("# Pipeline Run Version:\n")
                include_version_info(fh)
        fh.write("#### The end of for Copy Number Variant Calling ####\n")

    return True


def validate_args(args):
    """Arguments sanity check"""

    # Either one of title file or pairing file is required for this process
    if not args.title_file_path:
        raise Exception(
            "--title_file_path is required to determine tumor samples for copy number variant calling."
        )

    # Tumor bams folder is required for generating manifest list
    if not args.tumor_bams_directory:
        raise Exception(
            "--tumor_bams_directory is required for copy number variant calling."
        )

    if not args.output_file_name:
        raise Exception(
            "--output_file_name is required for copy number variant calling"
        )

    if not args.output_directory:
        raise Exception(
            "--output_directory is required for copy number variant calling"
        )


def main():
    """ Main """
    args = parse_arguments()
    create_inputs_file(args)
    return


if __name__ == "__main__":
    main()
