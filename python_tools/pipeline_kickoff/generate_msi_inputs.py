import os
import glob
import ast
import logging
import argparse
import ruamel.yaml
from collections import defaultdict

from python_tools.util import include_yaml_resources, include_version_info
from python_tools.constants import MSI_INPUTS, VERSION_PARAM

##########
# Pipeline Inputs generation for the ACCESS Copy Number Variant Calling
#
# Usage:
#
# generate_msi_inputs \
#   -sb ./standard_bams/ \
#   -o ./inputs.yaml \
#   -od ./outputs \
#   -p Project_Name \
#   -alone

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)
logger = logging.getLogger("msi_pipeline_kickoff")


# def parse_arguments():
#     """
#     Parse arguments for copy number calling pipeline inputs generation

#     :return: argparse.ArgumentParser object
#     """
#     parser = argparse.ArgumentParser()

#     parser.add_argument(
#         "-o",
#         "--output_file_name",
#         help="Filename for yaml file to be used as pipeline inputs",
#         required=True,
#     )

#     parser.add_argument("-p", "--project_name", help="project name", required=False)

#     parser.add_argument(
#         "-alone",
#         "--stand_alone",
#         help="Whether to run MSI as independent module",
#         nargs="?",
#         default=False,
#         const=True,
#         required=False,
#     )

#     parser.add_argument(
#         "-sb",
#         "--standard_bams_directory",
#         help="Directory that contains all standard bams to be used in MSI",
#         required=True,
#     )

#     parser.add_argument(
#         "-od",
#         "--output_directory",
#         help="Output Directory for MSI Caller",
#         required=True,
#     )

#     parser.add_argument(
#         "-td",
#         "--tmp_dir",
#         help="Absolute path to temporary working directory (e.g. /scratch)",
#         required=True,
#     )

#     args = parser.parse_args()
#     return args


def get_bam_dics(args, paired_df):
    """
    Retrieve bam list from given standard bam directory
    """
    tumorBamDic = {}
    normalBamDic = {}

    bam_list = glob.glob(os.path.join(args.standard_bams_directory, "*.bam"))
    for i, k in paired_df.iterrows():
        if k["normal_id"] == "":
            continue
        t_bam = [
            b for b in bam_list if os.path.basename(b).startswith(k["tumor_id"])
        ].pop()
        tumorBamDic[k["tumor_id"]] = t_bam
        n_bam = [
            b for b in bam_list if os.path.basename(b).startswith(k["normal_id"])
        ].pop()
        normalBamDic[k["normal_id"]] = n_bam

    return (tumorBamDic, normalBamDic)


def create_msi_inputs_file(args, paired_df):
    """
    Create the inputs.yaml file for the ACCESS MSI

    :param args: argparse.ArgumentParser object
    """
    # validate_args(args)

    (tumorBamDic, normalBamDic) = get_bam_dics(args, paired_df)
    if not tumorBamDic:
        raise Exception("Unable to get bam dics")

    path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    module = "cwl_tools/msi"
    if not args.project_name:
        projName = ""
    else:
        projName = args.project_name

    # Generate bam lists
    fileFormat = '{"class": "File", "path": "%s"}'
    inputYamlFileList = defaultdict(list)
    for (tumor, tumor_bam), (normal, normal_bam) in zip(
        tumorBamDic.items(), normalBamDic.items()
    ):
        inputYamlFileList["sample_name"].append(tumor)
        inputYamlFileList["tumor_bam"].append(ast.literal_eval(fileFormat % tumor_bam))
        inputYamlFileList["normal_bam"].append(
            ast.literal_eval(fileFormat % normal_bam)
        )

    inputYamlString = {
        "project_name": args.project_name or "",
        "file_path": os.path.join(path, module)
        # "msisensor_allele_counts": '{class: Directory, path: %s}' % args.output_directory
    }

    with open(os.path.join(args.output_directory, "msi.yaml"), "w") as fh:
        fh.write("#### Inputs for MSI ####\n\n")
        for item in inputYamlString:
            fh.write("{}: {}\n".format(item, inputYamlString[item]))
        fh.write("\n# File and Directory Inputs\n")

        for item in inputYamlFileList:
            fh.write(ruamel.yaml.dump({item: inputYamlFileList[item]}))
            fh.write("\n")

        include_yaml_resources(fh, MSI_INPUTS)
        fh.write("tmp_dir: {}\n".format(args.tmp_dir))

        try:
            include_yaml_resources(fh, VERSION_PARAM)
        except IOError:
            # that is if version.yaml is absent
            fh.write("# Pipeline Run Version:\n")
            include_version_info(fh)

    return True


# def validate_args(args):
#     """Arguments sanity check"""
#     # todo: should not be necessary

#     # Tumor bams folder is required for generating manifest list
#     if not args.standard_bams_directory:
#         raise Exception("--standard_bams_directory is required for MSI caller")

#     if not args.output_file_name:
#         raise Exception("--output_file_name is required for MSI caller")

#     if not args.output_directory:
#         raise Exception("--output_directory is required for MSI caller")


# def main():
#     """ Main """
#     args = parse_arguments()
#     create_inputs_file(args)
#     return


# if __name__ == "__main__":
#     main()
