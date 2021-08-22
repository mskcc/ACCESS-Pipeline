import os
import csv
import glob
import logging
import argparse
import ruamel.yaml

from python_tools.util import include_yaml_resources, include_version_info

from python_tools.constants import CNV_INPUTS, VERSION_PARAM

##########
# Pipeline Inputs generation for the ACCESS Copy Number Variant Calling
#
# Usage:
#
# generate_copynumber_inputs \
#   -t  ./title_file.txt \
#   -tb ./unfiltered_bams \
#   -o  inputs.yaml \
#   -od ./output \
#   -alone


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
        "-p", "--project_id", help="Unique identifier for this CNV run", required=True
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

    # parser.add_argument(
    #     '-e',
    #     '--engine_type',
    #     help='Type of engine the job will be submitting',
    #     required=False
    # )

    # parser.add_argument(
    #     '-q',
    #     '--queue',
    #     help='Queue used for job submitting',
    #     required=False
    # )

    parser.add_argument(
        "-od",
        "--output_directory",
        help="Output Directory for copy number variant calling",
        required=True,
    )

    parser.add_argument(
        "-td",
        "--tmp_dir",
        help="Absolute path to temporary working directory (e.g. /scratch)",
        required=True,
    )

    args = parser.parse_args()
    return args


def get_sampleID_and_sex(args, paired_df):
    """
    Retrieve sample IDs (samples with "-T*") and patient sex from title file
    """

    sample2sex = {}
    with open(args.title_file_path, "rU") as titleFile:
        tfDict = csv.DictReader(titleFile, delimiter="\t")
        for row in tfDict:
            if "Tumor" in row["Class"]:
                if "Sex" in row:
                    sex = row["Sex"].replace("Female", "Female").replace("Male", "Male")
                else:
                    sex = row["SEX"].replace("F", "Female").replace("M", "Male")

                if "Sample" in row:
                    sample2sex[row["Sample"]] = sex
                else:
                    sample2sex[row["CMO_SAMPLE_ID"]] = sex

    return sample2sex


def get_bam_list(args, paired_df):
    """
    Retrieve bam list from given tumor bam directory
    """
    tumor_bamList, normal_bamList = ([],) * 2
    all_tumor_bams = glob.glob(os.path.join(args.all_unique_bam_directory, "*.bam"))
    for i, k in paired_df.iterrows():
        #if k["normal_id"] == "":
        #    continue
        t_bam = [
            b for b in all_tumor_bams if os.path.basename(b).startswith(k["tumor_id"])
        ].pop()
        tumor_bamList.append(t_bam)
        # n_bam = [
        #     b for b in bam_list if os.path.basename(b).startswith(k["normal_id"])
        # ].pop()
        # normal_bamList.append(n_bam)

    return tumor_bamList


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


def create_cnv_inputs_file(args, paired_df):
    """
    Create the inputs.yaml file for the ACCESS Copy Number Variant Calling pipeline

    :param args: argparse.ArgumentParser object
    """

    sample2sex = get_sampleID_and_sex(args, paired_df)
    bamList = get_bam_list(args, paired_df)
    if not sample2sex or not bamList:
        raise Exception("Unable to load title file or get bam list")

    path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    module = "cwl_tools/cnv"

    inputYamlString = {
        "project_name": args.project_name,
        "file_path": os.path.join(path, module),
    }

    inputYamlOther = {
        "tumor_sample_list": {
            "class": "File",
            "path": generate_manifest_file(args, sample2sex, bamList),
        }
    }

    with open(os.path.join(args.output_directory, "inputs_cnv.yaml"), "w") as fh:
        fh.write("#### Inputs for Copy Number Variant Calling ####\n\n")
        for item in inputYamlString:
            fh.write("{}: {}\n".format(item, inputYamlString[item]))
        fh.write("\n# File and Directory Inputs\n")
        fh.write(ruamel.yaml.dump(inputYamlOther))

        include_yaml_resources(fh, CNV_INPUTS)

        # fh.write("tmp_dir: {}\n".format(args.tmp_dir))
        try:
            include_yaml_resources(fh, VERSION_PARAM)
        except IOError:
            # that is if version.yaml is absent
            fh.write("# Pipeline Run Version:\n")
            include_version_info(fh)


# def validate_args(args):
#     """Arguments sanity check"""

#     # Either one of title file or pairing file is required for this process
#     if not args.title_file_path:
#         raise Exception(
#             "--title_file_path is required to determine tumor samples for copy number variant calling."
#         )

#     # Tumor bams folder is required for generating manifest list
#     if not args.tumor_bams_directory:
#         raise Exception(
#             "--tumor_bams_directory is required for copy number variant calling."
#         )

#     if not args.output_directory
#         raise Exception(
#             "--output_file_name is required for copy number variant calling"
#         )

#     if not args.output_directory:
#         raise Exception(
#             "--output_directory is required for copy number variant calling"
#         )


def main():
    """ Main """
    args = parse_arguments()
    create_cnv_inputs_file(args)
    return


if __name__ == "__main__":
    main()
