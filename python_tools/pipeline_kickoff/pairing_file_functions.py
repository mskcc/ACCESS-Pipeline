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
    VARIANTS_INPUTS,
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


def generate_pairing_file(args):
    """
    Create T/N pairs from title file

    1. We allow grouping samples by either sample class (Tumor and Normal, Default) or sample type (Plasma and Buffycoat)
    2. Samples are paired based on common GROUP_BY_ID column in the title file

    :param title_file:
    :param pair_by: str
    :return paired_df: dict
    """
    tf = pd.read_csv(
        args.title_file_path, sep="\t", comment="#", header="infer", dtype=object
    )
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
