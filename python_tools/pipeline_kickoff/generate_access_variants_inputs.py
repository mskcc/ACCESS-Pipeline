import os
import re
import logging
import time
import subprocess
import argparse
import ruamel.yaml

import pandas as pd
import numpy as np

from python_tools.constants import (
    ACCESS_VARIANTS_RUN_FILES_PATH,
    ACCESS_VARIANTS_RUN_PARAMS_PATH,
    ACCESS_VARIANTS_RUN_TOOLS_PATH,
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
    ACCESS_VARIANTS_RUN_TOOLS_MANTA,
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


# Delimiter for inputs file sections
INPUTS_FILE_DELIMITER = "\n\n" + "# " + "--" * 30 + "\n\n"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
)
logger = logging.getLogger("access_variants_pipeline_kickoff")


def generate_pairing_file(args):
    """
    Create T/N pairs from title file

    1. We allow grouping samples by either sample class (Tumor and Normal, Default) or sample type (Plasma and Buffycoat)
    2. Samples are paired based on common GROUP_BY_ID column in the title file

    :param title_file:
    :param pair_by: str
    :return paired_df: dict
    """
    tf = pd.read_csv(args.title_file_path, sep="\t", comment="#", header="infer", dtype=object)
    tumor_samples = tf[~(tf["Class"] == "Normal")]["Sample"].values.tolist()

    # if coverage file is provided, drop low coverage samples.
    if args.coverage_file:
        coverage_df = pd.read_csv(args.coverage_file, header=0, sep="\t", dtype=object)
        samples_failing_coverage = coverage_df[
            (coverage_df["Duplex"].apply(float) <= args.mdcov)
            | (coverage_df["Simplex"].apply(float) <= args.mscov)
            | (coverage_df["All Unique"].apply(float) <= args.mucov)
            | (coverage_df["TotalCoverage"].apply(float) <= args.mtcov)
        ]["Sample"].values.tolist()

        # only select tumor samples
        samples_failing_coverage = list(
            set(samples_failing_coverage) & set(tumor_samples)
        )

        # Write out low coverage samples
        tf[tf["Sample"].isin(samples_failing_coverage)].to_csv(
            os.path.join(os.getcwd(), "samples_below_coverage_threshold.txt"),
            header=True,
            index=False,
            sep="\t",
        )

        # only retain samples that pass coverage requirement
        tf = tf[~(tf["Sample"].isin(samples_failing_coverage))]

    # Merge title file with itself to find T/N pairing
    tfmerged = pd.merge(tf, tf, on=GROUP_BY_ID, how="left")
    try:
        tfmerged = tfmerged[
            [
                SAMPLE_PAIR1,
                SAMPLE_PAIR2,
                GROUP_BY_ID,
                CLASS_PAIR1,
                CLASS_PAIR2,
                SAMPLE_TYPE_PAIR1,
                SAMPLE_TYPE_PAIR2,
            ]
        ]
    except KeyError:
        raise Exception(
            "Missing or unexpected column headers in {}. Title File should contain the following columns for successful pairing: {}".format(
                args.title_file_path, ", ".join(TITLE_FILE_PAIRING_EXPECTED_COLUMNS)
            )
        )

    # pair by either sample class (Tumor/normal), which is default, or sample type (plasma/buffy)
    if args.pair_by == SAMPLE_CLASS:
        paired = tfmerged[
            (tfmerged[CLASS_PAIR1] == TUMOR_CLASS)
            & (tfmerged[CLASS_PAIR2] == NORMAL_CLASS)
        ][[SAMPLE_PAIR1, SAMPLE_PAIR2, GROUP_BY_ID]]
        unpaired = tfmerged[
            (tfmerged[CLASS_PAIR1].isin([TUMOR_CLASS, "PoolTumor", "PoolNormal"]))
            & (~tfmerged[SAMPLE_PAIR1].isin(paired[SAMPLE_PAIR1].unique().tolist()))
        ][[SAMPLE_PAIR1, SAMPLE_PAIR2, GROUP_BY_ID]]
    else:
        paired = tfmerged[
            (tfmerged[SAMPLE_TYPE_PAIR1] == SAMPLE_TYPE_PLASMA)
            & (tfmerged[SAMPLE_TYPE_PAIR2] == SAMPLE_TYPE_NORMAL_NONPLASMA)
        ][[SAMPLE_PAIR1, SAMPLE_PAIR2, GROUP_BY_ID]]
        unpaired = tfmerged[
            (tfmerged[SAMPLE_TYPE_PAIR1] == SAMPLE_TYPE_PLASMA)
            & (~tfmerged[SAMPLE_PAIR1].isin(paired[SAMPLE_PAIR1].unique().tolist()))
        ][[SAMPLE_PAIR1, SAMPLE_PAIR2, GROUP_BY_ID]]
    unpaired[SAMPLE_PAIR2] = ""

    # Separate duplicated Tumors
    paired_dup = paired[paired.duplicated(subset=[SAMPLE_PAIR1], keep=False)]
    # Select T-N pair first based on sampleID suffix
    # For example TP01 will be paired with NB01, when multiple NBs are present for the sample TP.
    # If both NB01 and NB01rpt are present, NB01rpt will be chosen.
    paired_dup_select_by_suffix = (
        paired_dup[
            (
                paired_dup[SAMPLE_PAIR1].str.extract(
                    r"T[A-Za-z]*([0-9]+).*", expand=False
                )
                == paired_dup[SAMPLE_PAIR2].str.extract(
                    r"N[A-Za-z]*([0-9]+).*", expand=False
                )
            )
        ]
        .sort_values([SAMPLE_PAIR2])
        .drop_duplicates(subset=[SAMPLE_PAIR1], keep="last")
    )
    # For TPs for which NB cannot be chosen based on sampleID suffix, latest NB will be chosen. For example, NB02rpt will be chosen if NB01, NB02, NB02rpt are present for TP03
    paired_dup_select_by_latest_normal = (
        paired_dup[
            ~(paired_dup[SAMPLE_PAIR1].isin(paired_dup_select_by_suffix[SAMPLE_PAIR1]))
        ]
        .sort_values([SAMPLE_PAIR2])
        .drop_duplicates(subset=[SAMPLE_PAIR1], keep="last")
    )

    # Combine all the dfs
    paired_df = pd.concat(
        [
            paired[~(paired.duplicated(subset=[SAMPLE_PAIR1], keep=False))],
            paired_dup_select_by_suffix,
            paired_dup_select_by_latest_normal,
            unpaired,
        ]
    ).rename(
        index=str,
        columns={
            SAMPLE_PAIR1: TUMOR_ID,
            SAMPLE_PAIR2: NORMAL_ID,
            GROUP_BY_ID: GROUP_BY_ID,
        },
    )
    paired_df.to_csv(
        os.path.join(os.getcwd(), TITLE_FILE_TO_PAIRED_FILE),
        sep="\t",
        header=True,
        mode="w",
        index=False,
    )
    # If there are still duplciate Tumors, raise exception
    if paired_df.duplicated(subset=[TUMOR_ID], keep=False).any():
        raise Exception(
            "Duplicate Tumor sample entries in title file cannot be resolved. Please check {} for more information. Consider providing a Tumor Normal pairing file to override automatic pairing.".format(
                os.path.join(os.getcwd(), TITLE_FILE_TO_PAIRED_FILE)
            )
        )
    args.pairing_file_path = os.path.join(os.getcwd(), TITLE_FILE_TO_PAIRED_FILE)
    return tf, paired_df


def validate_pairing_file(pairing_file, tumor_samples, normal_samples):
    """
    Validate T/N pairs

    1. We allow normal_id to be blank in pairing file
    2. If normal_id is not blank, and id is not found in `normal_samples`, raise error
    3. Tumor ID can never be blank
    4. Tumor ID must be found in tumor_samples
    5. If both are found, continue

    :param pairing_file:
    :param tumor_samples: str[] of tumor bam files paths
    :param normal_samples: str[] of normal bam files paths
    :return:
    """
    for i, tn_pair in pairing_file.iterrows():
        tumor_id = tn_pair[TUMOR_ID]
        normal_id = tn_pair[NORMAL_ID]
        assert tumor_id, "Missing tumor sample ID in pairing file"

        # Find the path to the bam that contains this tumor sample ID
        tumor_sample = filter(
            lambda t: os.path.basename(t).startswith(
                tumor_id + SAMPLE_SEP_FASTQ_DELIMETER
            ),
            tumor_samples,
        )
        assert (
            len(tumor_sample) == 1
        ), "Incorrect # of matches for tumor sample {}".format(tumor_id)

        if normal_id and normal_id != "":
            normal_sample = filter(
                lambda n: normal_id + SAMPLE_SEP_FASTQ_DELIMETER in n, normal_samples
            )
            assert (
                len(normal_sample) == 1
            ), "Incorrect # of matches ({}) for paired normal for tumor sample {}".format(
                len(normal_sample), tumor_sample
            )


def parse_tumor_normal_pairing(
    pairing_file, tumor_samples, normal_samples, default_normal_path
):
    """
    Build tumor-normal pairs from pairing file and tumor / normal bam directories.

    Default to `default_normal_path` if matched normal not found.

    :param path:
    :return:
    """
    ordered_tumor_samples = []
    ordered_normal_samples = []
    ordered_fillout_samples = []
    # This flag will prevent us from trying to genotype the default normal more than once
    default_added_for_genotyping = False

    for i, tn_pair in pairing_file.iterrows():
        tumor_id = tn_pair["tumor_id"]
        normal_id = tn_pair["normal_id"]

        # Find the path to the bam that contains this tumor sample ID
        # (after pairing file validation this should return exactly 1 result)
        tumor_sample = filter(
            lambda t: os.path.basename(t).startswith(
                tumor_id + SAMPLE_SEP_FASTQ_DELIMETER
            ),
            tumor_samples,
        )
        assert (
            len(tumor_sample) == 1
        ), "Incorrect # of matches (matched = {}) for sammple ID {} in tumor_samples list.".format(
            str(len(tumor_sample)), tumor_id
        )
        tumor_sample = tumor_sample.pop()

        # Leaving the normal ID blank will cause the default normal to be used
        # Only tumor is used for genotyping
        if normal_id == "":
            ordered_tumor_samples.append(tumor_sample)
            ordered_normal_samples.append(default_normal_path)
            ordered_fillout_samples.append(tumor_sample)
            default_added_for_genotyping = True

            # if not default_added_for_genotyping:
            #     ordered_fillout_samples.append(default_normal_path)
            #     default_added_for_genotyping = True

        # Use the matching normal bam that contains this normal sample ID
        # Both samples are added for genotyping
        # TODO: make this else statement more specific
        elif any(normal_id in n for n in normal_samples):
            # matching_normal_samples = filter(lambda n: normal_id in n, normal_samples)
            matching_normal_sample = filter(
                lambda t: os.path.basename(t).startswith(
                    normal_id + SAMPLE_SEP_FASTQ_DELIMETER
                ),
                normal_samples,
            )
            assert (
                len(matching_normal_sample) == 1
            ), "Incorrect # of matches (matched = {}) for sammple ID {} in tumor_samples list.".format(
                str(len(matching_normal_sample)), normal_id
            )

            # if len(matching_normal_samples) > 1:
            # If we have multiple matches for this normal sample ID, make sure that they are exactly the same,
            # to avoid the following case: Sample_1 != Sample_1A
            # assert all([all([x == y for x in matching_normal_samples]) for y in matching_normal_samples])

            normal_sample = matching_normal_sample.pop()
            ordered_tumor_samples.append(tumor_sample)
            ordered_normal_samples.append(normal_sample)
            ordered_fillout_samples.append(tumor_sample)
            # Only genotype each normal once, even if it is paired with multiple tumors
            if not normal_sample in ordered_fillout_samples:
                ordered_fillout_samples.append(normal_sample)

    if default_added_for_genotyping:
        ordered_fillout_samples.append(default_normal_path)

    return ordered_tumor_samples, ordered_normal_samples, ordered_fillout_samples


def create_inputs_file(args):
    """
    Create the inputs.yaml file for the ACCESS Variant calling pipeline (modules 3 + 4)

    :param args: argparse.ArgumentParser object
    """
    validate_args(args)
    if args.pairing_file_path:
        pairing_df = pd.read_csv(
            args.pairing_file_path, sep="\t", comment="#", header="infer", dtype=object
        ).fillna("")
        title_file_df = pd.read_csv(
            args.title_file_path, sep="\t", comment="#", header="infer", dtype=object
        )
    else:
        try:
            title_file_df, pairing_df = generate_pairing_file(args)
        except (KeyError, ValueError, IndexError):
            print(
                "Cannot create Tumor Normal pairing file from {}".format(
                    args.title_file_path
                )
            )
            raise

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

    fh = open(args.output_file_name, "w")
    write_yaml_bams(
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
    )

    map(
        include_yaml_resources,
        [fh] * 3,
        [
            ACCESS_VARIANTS_RUN_FILES_PATH,
            ACCESS_VARIANTS_RUN_PARAMS_PATH,
            ACCESS_VARIANTS_RUN_TOOLS_PATH,
        ],
    )

    # Include sv related files
    include_sv_inputs(args, tumor_ids, fh)

    fh.write(INPUTS_FILE_DELIMITER)

    # Include traceback related files
    create_traceback_inputs(
        args, title_file_df, pairing_df, tumor_bam_paths, simplex_bam_paths, fh
    )

    ####### Generate inputs for CNV ########
    cmd = "generate_copynumber_inputs -t {title_file} -tb {bam_dir} -o {output_dir}/inputs_cnv.yaml -od {output_dir} -alone".format(
        title_file=args.title_file_path,
        bam_dir=args.all_unique_bam_directory,
        output_dir=os.path.dirname(args.output_file_name),
    )
    process = subprocess.Popen(cmd, shell=True, close_fds=True)
    process.wait()
    returncode = process.returncode
    if returncode == 0:
        time.sleep(3)
        cnv_yaml = os.path.join(
            os.path.dirname(args.output_file_name), "inputs_cnv.yaml"
        )
        # map(include_yaml_resources, [fh], [cnv_yaml])
    else:
        raise Exception("Unable to generate inputs yaml for cnv")
    ####### End of Generating inputs for CNV ########

    ####### Generate inputs for CNV ########
    cmd = "generate_msi_inputs -sb {bam_dir} -o {output_dir}/msi.yaml -od {output_dir} -alone".format(
        title_file=args.title_file_path,
        bam_dir=args.standard_bams_directory,
        output_dir=os.path.dirname(args.output_file_name),
    )
    process = subprocess.Popen(cmd, shell=True, close_fds=True)
    process.wait()
    returncode = process.returncode
    if returncode == 0:
        time.sleep(3)
        msi_yaml = os.path.join(os.path.dirname(args.output_file_name), "msi.yaml")
        # map(include_yaml_resources, [fh], [msi_yaml])
    else:
        raise Exception("Unable to generate inputs yaml for msi")
    ####### End of Generating inputs for CNV ########

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


def include_sv_inputs(args, tumor_ids, fh):
    """
    Write standard_bams files to inputs file, as well as SV parameters and tool paths from SV config files

    :param args: argparse.ArgumentsParser with parsed args
    :param fh: file handle for inputs file to write to
    :return:
    """

    standard_bams = find_bams_in_directory(args.standard_bams_directory, tumor_ids)
    standard_bams_yaml = create_yaml_file_objects(standard_bams)
    default_normal_yaml = {"class": "File", "path": args.default_stdnormal_path}
    sv_sample_id = [extract_sample_id_from_bam_path(b) for b in standard_bams]

    fh.write(INPUTS_FILE_DELIMITER)
    fh.write(ruamel.yaml.dump({"sv_sample_id": sv_sample_id}))
    fh.write(ruamel.yaml.dump({"sv_tumor_bams": standard_bams_yaml}))
    fh.write(ruamel.yaml.dump({"sv_normal_bam": default_normal_yaml}))

    include_yaml_resources(fh, ACCESS_VARIANTS_RUN_TOOLS_MANTA)


def validate_args(args):
    """Arguments sanity check"""

    # if T/N paired file is provided, it will be used instead of creating one from title file
    if args.pairing_file_path:
        print(
            "T/N pair file is provided. It will be directly used for analysis instead of generating one from title file."
        )

    # if a common project bam directory is provided, attempt to set any underfined
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
        #  and raise excpetion if they are missing.
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
    with open(ACCESS_VARIANTS_RUN_FILES_PATH, "r") as stream:
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
        "-o",
        "--output_file_name",
        help="Filename for yaml file to be used as pipeline inputs",
        required=True,
    )

    parser.add_argument(
        "-pn", "--project_name", help="Project name for this run", required=True
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
    create_inputs_file(args)


if __name__ == "__main__":
    main()
