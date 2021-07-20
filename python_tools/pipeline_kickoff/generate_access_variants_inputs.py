import os
import re
import logging
import time
import subprocess
import argparse
import ruamel.yaml

import pandas as pd
import numpy as np
from pairing_file_functions import (
    generate_pairing_file,
    validate_pairing_file,
    parse_tumor_normal_pairing,
)
from generate_copynumber_inputs import create_cnv_inputs_file

from generate_msi_inputs import create_msi_inputs_file

from python_tools.constants import (
    VARIANTS_INPUTS,
    CNV_INPUTS,
    SV_INPUTS,
    VERSION_PARAM,
    SAMPLE_SEP_FASTQ_DELIMETER,
    GROUP_BY_ID,
    SAMPLE_PAIR1,
    SAMPLE_PAIR2,
    CLASS_PAIR1,
    CLASS_PAIR2,
    SAMPLE_TYPE_PAIR1,
    SAMPLE_TYPE_PAIR2,
    TUMOR_CLASS,
    NORMAL_CLASS,
    SAMPLE_TYPE_PLASMA,
    SAMPLE_TYPE_NORMAL_NONPLASMA,
    SAMPLE_CLASS,
    TUMOR_ID,
    NORMAL_ID,
    TITLE_FILE_TO_PAIRED_FILE,
    TITLE_FILE__SAMPLE_CLASS_COLUMN,
    TITLE_FILE_PAIRING_EXPECTED_COLUMNS,
    STANDARD_BAM_DIR,
    UNFILTERED_BAM_DIR,
    SIMPLEX_BAM_DIR,
    DUPLEX_BAM_DIR,
    VERSION_PARAM,
)

from python_tools.util import (
    find_bams_in_directory,
    include_yaml_resources,
    include_version_info,
    create_yaml_file_objects,
    extract_sample_id_from_bam_path,
)


# Delimiter for inputs file sections
INPUTS_FILE_DELIMITER = "\n\n" + "# " + "--" * 30 + "\n\n"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)
logger = logging.getLogger("access_variants_pipeline_kickoff")


def create_vc_inputs_file(args, pairing_df, title_file_df):
    """
    Create the inputs.yaml file for the ACCESS Variant calling pipeline (modules 3 + 4)

    :param args: argparse.ArgumentParser object
    """
    tumor_ids, normal_ids, patient_ids = (
        filter(None, pairing_df[TUMOR_ID].tolist()),
        filter(None, pairing_df[NORMAL_ID].tolist()),
        filter(None, pairing_df[GROUP_BY_ID].tolist()),
    )
    tumor_bam_paths = find_bams_in_directory(args.tumor_bams_directory, tumor_ids)
    simplex_bam_paths = find_bams_in_directory(args.simplex_bams_directory, tumor_ids)
    curated_bam_duplex_paths = find_bams_in_directory(
        args.curated_bams_duplex_directory
    )
    curated_bam_simplex_paths = find_bams_in_directory(
        args.curated_bams_simplex_directory
    )

    # Normal bams paths are either from the bams directory, or repeating the default normal
    # Todo: remove! this logic should be based on the args.matched_mode param
    if args.normal_bams_directory:
        normal_bam_paths = find_bams_in_directory(
            args.normal_bams_directory, normal_ids
        )
    else:
        normal_bam_paths = [args.default_normal_path] * len(tumor_bam_paths)

    fh = open(os.path.join(args.output_directory, "VC_inputs.yaml"), "w")
    write_yaml_bams(
        fh,
        args,
        patient_ids,
        tumor_bam_paths,
        normal_bam_paths,
        simplex_bam_paths,
        curated_bam_duplex_paths,
        curated_bam_simplex_paths,
    )

    include_yaml_resources(fh, VARIANTS_INPUTS)

    # Include traceback related files
    create_traceback_inputs(
        args, title_file_df, pairing_df, tumor_bam_paths, simplex_bam_paths, fh
    )

    fh.write("title_file: {{class: File, path: {}}}\n".format(args.title_file_path))
    fh.write("project_name: {}".format(args.project_name))
    # Write the current pipeline version for this pipeline
    try:
        include_yaml_resources(fh, VERSION_PARAM)
    except IOError:
        # that is if version.yaml is absent
        fh.write(INPUTS_FILE_DELIMITER)
        fh.write("# Pipeline Run Version:\n")
        include_version_info(fh)
    fh.close()


def create_traceback_inputs(
    args, title_file_df, pairing_df, tumor_bam_paths, simplex_bam_paths, fh
):
    """
    Get traceback input mutations and bam file objects.
    """
    # tumor ids from title file and pairing file
    tumor_id = pairing_df[TUMOR_ID].values.tolist()
    title_file_df_select = title_file_df[title_file_df["Sample"].isin(tumor_id)]
    traceback_bams, traceback_samples = [], []

    # read traceback samples into a df and consume sampleIDs and file paths
    if args.traceback_samples:
        traceback_samples_df = pd.read_csv(
            args.traceback_samples, sep="\t", header=0, dtype=object
        )
        # Drop samples by Patient_ID in the df if the Patient_ID is absent in the pairing file
        traceback_samples_df = traceback_samples_df[
            traceback_samples_df["MRN"].isin(title_file_df_select[GROUP_BY_ID])
        ]
        traceback_mutations_df = pd.read_csv(
            args.traceback_mutations, sep="\t", header=0, dtype=object
        )
        # check that one of traceback_samples.txt and traceback_input_mutations.txt
        #  is not empty while the other has data.
        if traceback_samples_df.empty ^ traceback_mutations_df.empty:
            raise Exception(
                "One of {} or {} has no data. Please check that both files are populated correctly.\n".format(
                    "traceback_samples.txt", "traceback_input_mutations.txt"
                )
            )
        # Determine bam type
        traceback_samples_df["BAM_TYPE"] = traceback_samples_df["BAM_file_path"].apply(
            lambda x: "DUPLEX"
            if "-duplex" in os.path.basename(x)
            else ("SIMPLEX" if "-simplex" in os.path.basename(x) else "STANDARD")
        )

        traceback_bams.extend(traceback_samples_df["BAM_file_path"].values.tolist())
        traceback_samples.extend(
            (
                traceback_samples_df["Sample"] + "_" + traceback_samples_df["BAM_TYPE"]
            ).values.tolist()
        )
    # duplex bams from current project
    traceback_bams.extend(
        list(
            filter(
                lambda x: extract_sample_id_from_bam_path(x) in tumor_id,
                tumor_bam_paths,
            )
        )
    )
    traceback_samples.extend(
        map(
            lambda x: str(x) + "_DUPLEX",
            list(
                filter(
                    lambda x: x in tumor_id,
                    [extract_sample_id_from_bam_path(x) for x in tumor_bam_paths],
                )
            ),
        )
    )
    # simplex bams from current project
    traceback_bams.extend(
        list(
            filter(
                lambda x: extract_sample_id_from_bam_path(x) in tumor_id,
                simplex_bam_paths,
            )
        )
    )
    traceback_samples.extend(
        map(
            lambda x: str(x) + "_SIMPLEX",
            list(
                filter(
                    lambda x: x in tumor_id,
                    [extract_sample_id_from_bam_path(x) for x in simplex_bam_paths],
                )
            ),
        )
    )
    # create traceback yaml objects
    traceback_bams = create_yaml_file_objects(traceback_bams)

    # traceback_data = {
    #     "traceback": {
    #         "traceback_mutation_file: {class: File, path: \{}": str(args.traceback_mutations or ""),
    #         "bam_files": traceback_bams,
    #         "ids": traceback_samples,
    #     }
    # }
    # fh.write(ruamel.yaml.dump(traceback_data, indent=2))
    fh.write("#Traceback:\n")
    fh.write(
        "traceback_mutation_file: {{class: File, path: {}}}\n".format(
            str(args.traceback_mutations)
        )
    )
    fh.write(ruamel.yaml.dump({"traceback_sample_ids": traceback_samples}))
    fh.write(ruamel.yaml.dump({"traceback_bams": traceback_bams}))
    fh.write(INPUTS_FILE_DELIMITER)


def write_yaml_bams(
    fh,
    args,
    # tumor_ids,
    # normal_ids,
    patient_ids,
    tumor_bam_paths,
    normal_bam_paths,
    simplex_bam_paths,
    curated_bam_duplex_paths,
    curated_bam_simplex_paths,
):
    """
    Write the lists of tumor, normal, and genotyping bams to the inputs file, along with their sample IDs
    Todo: clean this up a bit

    :param fh: inputs file file handle
    :param args: argparse.ArgumentParser object with bam directory attribute
    :return:
    """

    # 1. Build lists of bams
    if args.pairing_file_path:
        pairing_file = pd.read_csv(
            args.pairing_file_path, sep="\t", comment="#", header="infer", dtype=object
        ).fillna("")
        validate_pairing_file(pairing_file, tumor_bam_paths, normal_bam_paths)

        ordered_tumor_bams, ordered_normal_bams, ordered_tn_genotyping_bams = parse_tumor_normal_pairing(
            pairing_file, tumor_bam_paths, normal_bam_paths, args.default_normal_path
        )

        if not args.matched_mode:
            # If we aren't in matched mode, do variant calling with default normal
            # (pairing file is only used for genotyping)
            ordered_normal_bams = [args.default_normal_path] * len(tumor_bam_paths)
            # Todo: Need to genotype default normal?
            # ordered_tn_genotyping_bams = ordered_tn_genotyping_bams + [args.default_normal_path]

        matched_normal_ids = [n for n in pairing_file["normal_id"]]
        matched_normal_ids = [
            correct_sample_id(n, normal_bam_paths) if n else ""
            for n in matched_normal_ids
        ]
    else:
        # In unmatched mode, the sample pairing is much simpler (just use the supplied default normal)
        ordered_tumor_bams = tumor_bam_paths
        ordered_normal_bams = [args.default_normal_path] * len(tumor_bam_paths)
        # Only add the default normal once
        ordered_tn_genotyping_bams = ordered_tumor_bams + [args.default_normal_path]
        matched_normal_ids = [""] * len(ordered_tumor_bams)

    # 2. Build lists of Sample IDs
    if args.matched_mode:
        # Use pairing file in matched mode
        tumor_sample_ids = [
            correct_sample_id(t, ordered_tumor_bams) for t in pairing_file["tumor_id"]
        ]
        normal_sample_ids = [
            n if n else extract_sample_id_from_bam_path(args.default_normal_path)
            for n in pairing_file["normal_id"]
        ]
    elif args.pairing_file_path:
        # Use pairing file in matched mode
        tumor_sample_ids = [
            correct_sample_id(t, ordered_tumor_bams) for t in pairing_file["tumor_id"]
        ]
        normal_sample_ids = [
            extract_sample_id_from_bam_path(args.default_normal_path)
        ] * len(tumor_sample_ids)
    else:
        # Otherwise use default normal
        tumor_sample_ids = [extract_sample_id_from_bam_path(b) for b in tumor_bam_paths]
        normal_sample_ids = [
            extract_sample_id_from_bam_path(args.default_normal_path)
        ] * len(tumor_sample_ids)

    # 3. Convert bam paths to CWL File objects
    tumor_bams, normal_bams, tn_genotyping_bams, simplex_genotyping_bams, curated_duplex_genotyping_bams, curated_simplex_genotyping_bams = map(
        create_yaml_file_objects,
        [
            ordered_tumor_bams,
            ordered_normal_bams,
            ordered_tn_genotyping_bams,
            simplex_bam_paths,
            curated_bam_duplex_paths,
            curated_bam_simplex_paths,
        ],
    )

    # 4. Genotyping sample IDs must be extracted from the bams themselves
    merged_tn_sample_ids = [
        extract_sample_id_from_bam_path(b["path"]) for b in tn_genotyping_bams
    ]
    simplex_genotyping_ids = [
        extract_sample_id_from_bam_path(b["path"]) + "-SIMPLEX"
        for b in simplex_genotyping_bams
    ]
    curated_duplex_genotyping_ids = [
        extract_sample_id_from_bam_path(b["path"]) + "-CURATED-DUPLEX"
        for b in curated_duplex_genotyping_bams
    ]
    curated_simplex_genotyping_ids = [
        extract_sample_id_from_bam_path(b["path"]) + "-CURATED-SIMPLEX"
        for b in curated_simplex_genotyping_bams
    ]

    genotyping_bams = (
        tn_genotyping_bams
        + simplex_genotyping_bams
        + curated_duplex_genotyping_bams
        + curated_simplex_genotyping_bams
    )
    genotyping_bams_ids = (
        merged_tn_sample_ids
        + simplex_genotyping_ids
        + curated_duplex_genotyping_ids
        + curated_simplex_genotyping_ids
    )

    genotyping_bams_ids = {"genotyping_bams_ids": genotyping_bams_ids}
    tumor_bam_paths = {"tumor_bams": tumor_bams}
    normal_bam_paths = {"normal_bams": normal_bams}
    tumor_sample_ids = {"tumor_sample_names": tumor_sample_ids}
    normal_sample_ids = {"normal_sample_names": normal_sample_ids}
    matched_normal_ids = {"matched_normal_ids": matched_normal_ids}
    patient_ids = {"patient_ids": patient_ids}
    genotyping_bams_paths = {"genotyping_bams": genotyping_bams}

    # 5. Write them to the inputs yaml file
    fh.write(ruamel.yaml.dump(tumor_bam_paths))
    fh.write(ruamel.yaml.dump(normal_bam_paths))
    fh.write(ruamel.yaml.dump(tumor_sample_ids))
    fh.write(ruamel.yaml.dump(normal_sample_ids))
    fh.write(ruamel.yaml.dump(matched_normal_ids))
    fh.write(ruamel.yaml.dump(patient_ids))
    fh.write(ruamel.yaml.dump(genotyping_bams_paths))
    fh.write(ruamel.yaml.dump(genotyping_bams_ids))


def correct_sample_id(query_sample_id, bam_paths):
    """
    Compare `query_sample_id` to each element in bam_paths, and extract the actual sample ID from that bam's path

    :param query_sample_id: str - sample ID to be found in exactly one entry from `bam_paths`
    :param bam_paths: str[] - bam file paths to search through
    :return:
    """
    matches = filter(
        lambda b: os.path.basename(b).startswith(
            query_sample_id + SAMPLE_SEP_FASTQ_DELIMETER
        ),
        bam_paths,
    )
    assert len(matches) == 1, "Incorrect # of matches for sample ID {}".format(
        query_sample_id
    )

    matching_bam_path = matches.pop()
    return extract_sample_id_from_bam_path(matching_bam_path)


def create_sv_inputs_file(args, paired_df):
    """
    Write standard_bams files to inputs file, as well as SV parameters and tool paths from SV config files

    :param args: argparse.ArgumentsParser with parsed args
    :param fh: file handle for inputs file to write to
    :return:
    """
    with open(os.path.join(args.output_directory, "SV.yaml"), "w") as fh:
        standard_bams = find_bams_in_directory(
            args.standard_bams_directory, paired_df[TUMOR_ID].tolist()
        )
        standard_bams_yaml = create_yaml_file_objects(standard_bams)
        default_normal_yaml = {"class": "File", "path": args.default_stdnormal_path}
        sv_sample_id = [extract_sample_id_from_bam_path(b) for b in standard_bams]

        fh.write(ruamel.yaml.dump({"sv_sample_id": sv_sample_id}))
        fh.write(ruamel.yaml.dump({"sv_tumor_bams": standard_bams_yaml}))
        fh.write(ruamel.yaml.dump({"sv_normal_bam": default_normal_yaml}))

        include_yaml_resources(fh, SV_INPUTS)
        fh.write("project_name: {}\n".format(args.project_name))
        fh.write("tmp_dir: {}\n".format(args.tmp_dir))

        try:
            include_yaml_resources(fh, VERSION_PARAM)
        except IOError:
            # that is if version.yaml is absent
            fh.write("# Pipeline Run Version:\n")
            include_version_info(fh)


def validate_args(args):
    """Arguments sanity check"""

    # if T/N paired file is provided, it will be used instead of creating one from title file
    if args.pairing_file_path:
        print(
            "T/N pair file is provided. It will be directly used for analysis instead of generating one from title file."
        )

    # if a common project bam directory is provided, attempt to set any undefined
    #  path to each of the duplex, simplex, unfiltered, and standard bam directories.
    if args.bam_project_directory:
        expected_bam_subdir = [
            STANDARD_BAM_DIR,
            UNFILTERED_BAM_DIR,
            SIMPLEX_BAM_DIR,
            DUPLEX_BAM_DIR,
            UNFILTERED_BAM_DIR,
        ]
        bam_dir_arg_attributes = [
            "standard_bams_directory",
            "all_unique_bam_directory",
            "simplex_bams_directory",
            "tumor_bams_directory",
            "normal_bams_directory",
        ]

        # if sub-directories are not defined in args, use expected sub-directory names
        #  and raise exception if they are missing.
        for index, attribute in enumerate(bam_dir_arg_attributes):
            if getattr(args, attribute) is None:
                setattr(
                    args,
                    attribute,
                    os.path.join(
                        args.bam_project_directory, expected_bam_subdir[index]
                    ),
                )

            if not os.path.isdir(getattr(args, attribute)):
                raise OSError(
                    "No such file or directory: {}. Please define --{}".format(
                        getattr(args, attribute), attribute
                    )
                )

    # check for reference files and directories in reference yaml files and args
    with open(VARIANTS_INPUTS, "r") as stream:
        run_files = ruamel.yaml.round_trip_load(stream)
        try:
            args.default_stdnormal_path = (
                args.default_stdnormal_path
                or run_files.get("reference_bam_for_SV")["path"]
            )
        except (KeyError, TypeError):
            # if not defined in the yaml file, it will be set as None
            pass
        try:
            args.default_normal_path = (
                args.default_normal_path
                or run_files.get("reference_bam_for_VC")["path"]
            )
        except (KeyError, TypeError):
            # if not defined in the yaml file, it will be set as None
            pass
        try:
            args.curated_bams_duplex_directory = (
                args.curated_bams_duplex_directory
                or run_files.get("curated_duplex_bams")[args.seq_machine]["path"]
            )
        except (KeyError, TypeError):
            # if not defined in the yaml file, it will be set as None
            pass
        try:
            args.curated_bams_simplex_directory = (
                args.curated_bams_simplex_directory
                or run_files.get("curated_simplex_bams")[args.seq_machine]["path"]
            )
        except (KeyError, TypeError):
            # if not defined in the yaml file, it will be set as None
            pass

    # Normal bams folder is required in matched mode
    if args.matched_mode and args.normal_bams_directory is None:
        raise Exception("--matched_mode requires --normal_bams_directory")

    # If structural varint calling is enabled, a control standard bam is required, for unmatched variant calling.
    if args.standard_bams_directory and not args.default_stdnormal_path:
        raise Exception(
            "--default_stdnormal_path should be also provided when --standard_bams_directory is defined."
        )


def parse_arguments():
    """
    Parse arguments for Variant calling pipeline inputs generation

    :return: argparse.ArgumentParser object
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-od", "--output_directory", help="output_directory", required=True
    )

    parser.add_argument(
        "-pn", "--project_name", help="Project name for this run", required=True
    )

    parser.add_argument(
        "-i",
        "--create_inputs",
        choices=["all", "vc", "cnv", "sv", "msi"],
        default="all",
        help="create input yaml for all or one of the analyses",
        required=False,
    )

    parser.add_argument(
        "-m",
        "--matched_mode",
        action="store_true",
        help="Create inputs from matched T/N pairs (True), or use default Normal (False)",
        required=False,
    )

    parser.add_argument(
        "-t", "--title_file_path", help="title file in tsv format", required=True
    )

    parser.add_argument(
        "-pb",
        "--pair_by",
        choices=["class", "type"],
        default="class",
        help="pair samples in title file by sample class (Tumor:Normal) or sample type (Plamsa:Buffcoat)",
        required=False,
    )

    parser.add_argument(
        "-p",
        "--pairing_file_path",
        help="tsv file with tumor sample IDs mapped to normal sample IDs",
        required=False,
    )

    parser.add_argument(
        "-dn",
        "--default_normal_path",
        help="Normal used in unmatched mode, or in matched mode if no matching normal found for tumor sample",
        required=False,
    )

    parser.add_argument(
        "-b",
        "--bam_project_directory",
        help="Main project directory that contains all tumor and normal bams",
        required=False,
    )

    parser.add_argument(
        "-tb",
        "--tumor_bams_directory",
        help="Directory that contains all tumor bams to be used in variant calling",
        required=False,
    )

    parser.add_argument(
        "-nb",
        "--normal_bams_directory",
        help="Directory that contains all normal bams to be used in variant calling and genotyping "
        "(if using matched mode, otherwise only used for genotyping)",
        required=False,
    )

    parser.add_argument(
        "-sb",
        "--simplex_bams_directory",
        help="Directory that contains additional simplex bams to be used for genotyping",
        required=False,
    )

    # Note: For ACCESS, we will often genotype from the same folders of curated bams
    parser.add_argument(
        "-cbd",
        "--curated_bams_duplex_directory",
        help="Directory that contains additional duplex curated bams to be used for genotyping",
        required=False,
    )

    parser.add_argument(
        "-cbs",
        "--curated_bams_simplex_directory",
        help="Directory that contains additional simplex curated bams to be used for genotyping",
        required=False,
    )

    parser.add_argument(
        "-stdb",
        "--standard_bams_directory",
        help="""If you would like SV calling, this is the directory that contains standard bams
         to be paired with the default normal. Note: This argument is to be paired with 
         the ACCESS_Variants.cwl workflow.""",
        required=False,
    )

    parser.add_argument(
        "-dstdn",
        "--default_stdnormal_path",
        help="Normal used in unmatched mode for structural variant calling",
        required=False,
    )

    parser.add_argument(
        "-tmi",
        "--traceback_mutations",
        help="Mutation data for any relevant prior samples",
        required=False,
    )

    parser.add_argument(
        "-ts",
        "--traceback_samples",
        help="Sample list with bam file paths for any relevant prior samples",
        required=False,
    )

    parser.add_argument(
        "-aub",
        "--all_unique_bam_directory",
        help="Bam file paths for all unique bam files",
        required=False,
    )

    parser.add_argument(
        "-td",
        "--tmp_dir",
        dest="tmp_dir",
        default="/dmp/analysis/SCRATCH/",
        help="Tmp directory path",
        required=False,
    )

    parser.add_argument(
        "-sm",
        "--seq_machine",
        help="Sequencing machine used",
        choices=["novaseq", "hiseq"],
        default="novaseq",
        required=False,
    )

    parser.add_argument(
        "-cf", "--coverage_file", help="panelA coverage file", required=False
    )

    parser.add_argument(
        "-mdcov",
        "--min_duplex_coverage",
        help="Min duplex coverage to perform analysis on a sample",
        dest="mdcov",
        default=150,
        required=False,
    )

    parser.add_argument(
        "-mscov",
        "--min_simplex_coverage",
        help="Min simplex coverage to perform analysis on a sample",
        dest="mscov",
        default=0,
        required=False,
    )

    parser.add_argument(
        "-mucov",
        "--min_unique_coverage",
        help="Min all unique coverage to perform analysis on a sample",
        dest="mucov",
        default=200,
        required=False,
    )

    parser.add_argument(
        "-mtcov",
        "--min_total_coverage",
        help="Min standard/total coverage to perform analysis on a sample",
        dest="mtcov",
        default=500,
        required=False,
    )

    args = parser.parse_args()

    return args


def main():
    """ Main """
    args = parse_arguments()
    validate_args(args)
    if not args.pairing_file_path:
        tf, paired_df = generate_pairing_file(args)
    if args.create_inputs == "vc":
        create_vc_inputs_file(args, paired_df, tf)
    elif args.create_inputs == "cnv":
        create_cnv_inputs_file(args, paired_df)
    elif args.create_inputs == "msi":
        create_msi_inputs_file(args, paired_df)
    elif args.create_inputs == "sv":
        create_sv_inputs_file(args, paired_df)
    else:
        create_vc_inputs_file(args, paired_df, tf)
        create_cnv_inputs_file(args, paired_df)
        create_msi_inputs_file(args, paired_df)
        create_sv_inputs_file(args, paired_df)


if __name__ == "__main__":
    main()
