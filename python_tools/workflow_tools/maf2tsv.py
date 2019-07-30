#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import errno
import pandas as pd
import numpy as np
import re

from constants import (
    MAF_COLUMNS_SELECT,
    MAF_TSV_COL_MAP,
    ALLOWED_EXONIC_VARIANT_CLASS,
    EXONIC_DROPPED,
    EXONIC_FILTERED,
    SILENT_DROPPED,
    SILENT_FILTERED,
    NONPANEL_EXONIC_DROPPED,
    NONPANEL_EXONIC_FILTERED,
    NONPANEL_SILENT_DROPPED,
    NONPANEL_SILENT_FILTERED,
    IS_EXONIC_CLASS,
    MAF_DUMMY_COLUMNS,
    MAF_DUMMY_COLUMNS2,
    GNOMAD_COLUMNS,
)


def add_dummy_columns(maf, columns):
    """
    Temporary function to add dummy columns
    to meet DMP requirements
    """
    for col in columns:
        if not col in maf.columns:
            maf[col] = ""
    return maf


def maf2tsv(maf_file):
    """
    Select the most useful columns and map
    the columns to a different naming confirmation.
    """

    def get_exon(maf_exon, maf_intron):
        """"
        helper function to determine the exonic or
        intronic location of a variant.
        """
        try:
            exon, total_exon = str(maf_exon).split("/")
            return "exon" + str(exon)
        except ValueError:  # Not exonic
            try:
                intron, total_intron = str(maf_intron).split("/")
                return "intron" + str(intron)
            except ValueError:  # Not intronic
                return ""

    try:
        maf = pd.read_csv(maf_file, sep="\t", header=0)
    except IOError:
        raise

    # Replace "-" in column headers to "_" so that they can be
    #  used as attributes to a variant object
    incompatible_required_column_headers = filter(
        lambda x: "-" in x and any([x.startswith("CURATED-"), x.startswith("NORMAL-")]),
        maf.columns,
    )
    maf = maf.rename(
        columns=dict(
            zip(
                incompatible_required_column_headers,
                map(
                    lambda x: x.replace("-", "_"), incompatible_required_column_headers
                ),
            )
        )
    )

    # assign potential missing expected columns in MAF
    # TODO: this can be removed once vep output is fixed
    #  with gnomad output
    maf = add_dummy_columns(maf, MAF_DUMMY_COLUMNS2)

    # if a mutation does not have a flag for "Mutation_Status", classify it as Novel
    maf["Mutation_Class"] = maf["Mutation_Status"].apply(lambda x: "" if x else "Novel")

    try:
        maf = maf[MAF_COLUMNS_SELECT]
    except KeyError:
        missing_columns = set(MAF_COLUMNS_SELECT) - set(maf.columns.values.tolist())
        raise Exception(
            "Following required columns are missing in the {}: {}".format(
                maf_file, ",".join(missing_columns)
            )
        )

    # compute columns
    maf["EXON"] = np.vectorize(get_exon, otypes=[str])(maf["EXON"], maf["INTRON"])
    maf = maf.drop(["INTRON"], axis=1)

    # Compute columns
    # maf = maf.rename(index=str, columns=MAF_TSV_COL_MAP)
    # get max of gnomad
    maf["gnomAD_Max_AF"] = np.nanmax(maf[GNOMAD_COLUMNS].values, axis=1)

    # compute various mutation depth and vaf metrics
    maf["D_t_count_fragment"] = (
        maf["D_t_ref_count_fragment"] + maf["D_t_alt_count_fragment"]
    )
    maf["SD_t_count_fragment"] = (
        maf["SD_t_ref_count_fragment"] + maf["SD_t_alt_count_fragment"]
    )
    maf["S_t_ref_count_fragment"] = (
        maf["SD_t_ref_count_fragment"] - maf["D_t_ref_count_fragment"]
    )
    maf["S_t_alt_count_fragment"] = (
        maf["SD_t_alt_count_fragment"] - maf["D_t_alt_count_fragment"]
    )
    maf["S_t_count_fragment"] = (
        maf["S_t_ref_count_fragment"] + maf["S_t_alt_count_fragment"]
    )
    maf["n_count_fragment"] = maf["n_ref_count_fragment"] + maf["n_alt_count_fragment"]
    maf["S_t_vaf_fragment"] = (
        maf["S_t_alt_count_fragment"] / maf["S_t_count_fragment"]
    ).fillna(0)
    maf["SD_t_vaf_fragment_over_n_vaf_fragment"] = (
        maf["SD_t_vaf_fragment"] / maf["n_vaf_fragment"]
    ).fillna(0)

    # convert NaN and inf computed values to 0
    maf = maf.replace([np.inf, np.nan], 0)

    # format SNP column
    maf["dbSNP_RS"] = maf["dbSNP_RS"].apply(
        lambda x: x if isinstance(x, str) and x.startswith("rs") else ""
    )

    # generate occurrence stats columns
    maf["CURATED_DUPLEX_n_fillout_sample"] = (
        maf["CURATED_DUPLEX_n_fillout_sample_alt_detect"].map(str)
        + ";"
        + maf["CURATED_DUPLEX_median_VAF"].map(str)
    )
    maf["CURATED_SIMPLEX_DUPLEX_n_fillout_sample"] = (
        maf["CURATED_SIMPLEX_DUPLEX_n_fillout_sample_alt_detect"].map(str)
        + ";"
        + maf["CURATED_SIMPLEX_DUPLEX_median_VAF"].map(str)
    )
    maf["NORMAL_n_fillout_sample"] = (
        maf["NORMAL_n_fillout_sample_alt_detect"].map(str)
        + ";"
        + maf["NORMAL_median_VAF"].map(str)
    )
    return maf


def filter_maf(maf, ref_tx_file, project_name, outdir):
    """
    Parse a dataframe of annotated variants, add any required columns and 
    classify them into exonic, silent, or nonpanel
    """
    # Get transcript list from the user provided file
    try:
        tx = pd.read_csv(
            ref_tx_file,
            header=0,
            sep="\t",
            usecols=["isoform", "gene_name", "refseq_id"],
        )
    except IOError:
        raise
    except KeyError:
        raise Exception(
            "Transcript file requires the following columns {}.".format(
                ",".join(["isoform", "gene_name", "refseq_id"])
            )
        )
    tx_list = tx.isoform.values.tolist()

    def format_var(variant):
        """
        Helper function to convert named tuple dervied from pandas df into tsv
        """
        try:
            columns = map(lambda x: getattr(variant, x), MAF_TSV_COL_MAP.keys())
            return "\t".join(map(str, columns)) + "\n"
        except AttributeError:
            missing_columns = set(MAF_TSV_COL_MAP.keys()) - set(
                filter(lambda x: not x.startswith("_"), dir(variant))
            )
            raise Exception(
                "Missing required columns: {}".format(",".join(missing_columns))
            )

    def reformat_tx(txID, tx_df=tx):
        """
        helper function to get reportable txID
        """
        return tx_df[tx_df.isoform == txID].refseq_id.values.tolist().pop()

    # TODO: This dummy columns block is to be removed at some point
    maf = add_dummy_columns(maf, MAF_DUMMY_COLUMNS)

    # Create exonic, silent, and nonpanel files.
    with open(outdir + "/" + project_name + EXONIC_FILTERED, "w") as ef, open(
        outdir + "/" + project_name + EXONIC_DROPPED, "w"
    ) as ed, open(outdir + "/" + project_name + SILENT_FILTERED, "w") as sf, open(
        outdir + "/" + project_name + SILENT_DROPPED, "w"
    ) as sd, open(
        outdir + "/" + project_name + NONPANEL_EXONIC_FILTERED, "w"
    ) as nef, open(
        outdir + "/" + project_name + NONPANEL_EXONIC_DROPPED, "w"
    ) as ned, open(
        outdir + "/" + project_name + NONPANEL_SILENT_FILTERED, "w"
    ) as nsf, open(
        outdir + "/" + project_name + NONPANEL_SILENT_DROPPED, "w"
    ) as nsd:

        # Print headers
        map(
            lambda f: f.write("\t".join(MAF_TSV_COL_MAP.values()) + "\n"),
            [ef, ed, sf, sd, nsf, nsd, nef, ned],
        )

        # Iterate over the maf file and determine status of each variant
        for variant in maf.itertuples():
            # set flag to classify if a variant is exonic
            is_exonic = IS_EXONIC_CLASS(
                variant.Hugo_Symbol, variant.Variant_Classification, variant.VCF_POS
            )
            # classify non-panel and non-canonical variants to filtered and dropped files
            if variant.Transcript_ID not in tx_list:
                if variant.Status and is_exonic:
                    ned.write(format_var(variant))
                elif variant.Status:
                    nsd.write(format_var(variant))
                elif is_exonic:
                    nef.write(format(variant))
                else:
                    nsf.write(format(variant))
           # exonic variants
            elif is_exonic:
                variant_tuple = is_exonic
                variant = variant._replace(
                    Hugo_Symbol=variant_tuple[0],  # Gene
                    Variant_Classification=variant_tuple[1],  # VariantClass
                    VCF_POS=variant_tuple[2],  # Start coordinate
                    Transcript_ID=reformat_tx(variant.Transcript_ID),  # TranscriptID
                )
                if variant.Status:
                    ed.write(format_var(variant))
                else:
                    ef.write(format_var(variant))
            # silent variants
            else:
                variant = variant._replace(
                    Transcript_ID=reformat_tx(variant.Transcript_ID)
                )
                if variant.Status:
                    sd.write(format_var(variant))
                else:
                    sf.write(format_var(variant))


def get_project(titlefile):
    """
    get project name form title file
    """
    try:
        title_file = pd.read_csv(
            titlefile, sep="\t", header=0, usecols=["Sample", "Pool"]
        )
    except IOError:
        raise
    except KeyError:
        raise Exception(
            "The title file provided should include 'Sample' and 'Project' columns."
        )

    project_name = set(title_file["Pool"].values.tolist())
    if len(project_name) > 1:
        raise Exception(
            "Title file has multiple project names {}. Should be an unique project name.".format(
                ",".join(project_name)
            )
        )
    return project_name.pop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--anno_maf",
        help="MAF from Remove Variants module that has all the annotations required in the final MAF",
        required=True,
    )
    parser.add_argument("--title_file", help="Tile file for the project", required=True)
    parser.add_argument("--project_name", help="Project Name", required=False)
    parser.add_argument(
        "--canonical_tx_ref", help="Reference canonical transcript file", required=True
    )
    parser.add_argument(
        "--outdir",
        help="Directory for storing the final files; Default = pwd)",
        required=False,
    )

    args = parser.parse_args()

    # Resolve args
    if not args.project_name:
        args.project_name = get_project(args.title_file)
    if not args.outdir:
        args.outdir = os.getcwd()

    try:
        os.mkdir(os.path.abspath(args.outdir))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # Filter and categorize variants
    condensed_maf = maf2tsv(args.anno_maf)
    filter_maf(condensed_maf, args.canonical_tx_ref, args.project_name, args.outdir)


if __name__ == "__main__":
    main()
