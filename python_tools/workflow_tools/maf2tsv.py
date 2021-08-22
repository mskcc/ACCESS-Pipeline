#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import errno
import pandas as pd
import numpy as np
import re

from python_tools.constants import (
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
    GENE_BASED_FILTER,
    MUTATION_STATUS_BASED_FILTER,
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

    def get_exon(maf_exon, maf_intron, maf_cdna, maf_variant_class):
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
                if maf_variant_class in ["Splice_Site", "Splice_Region"]:
                    # if the variant spans an entire exon, do not impute
                    #  exon number
                    if "+" in maf_cdna and "-" in maf_cdna:
                        return ""
                    elif "+" in maf_cdna:
                        return "exon" + str(intron)
                    elif "-" in maf_cdna:
                        return "exon" + str(int(intron) + 1)
                    # if cannot impute exon number, return intron
                    else:
                        return "intron" + str(intron)
            except (TypeError, ValueError):  # Not intronic
                return ""

    def customize_cosmic(cosmic_id, cosmic_occurrence):
        """
        helper function to customize cosmic annotation.
        If cosmic_id is defined, but not occurrence, then
        a generic value of "1(unknown)" will be used.
        """
        if cosmic_id is not np.nan and cosmic_id != "":
            # OCCURENCE spelled incorrectly by design
            return (
                "ID="
                + cosmic_id
                + ";OCCURENCE="
                + (
                    cosmic_occurrence
                    if cosmic_occurrence is not np.nan
                    else "1(unknown)"
                )
            )
        else:
            return ""

    # Read in the mutation maf
    try:
        maf = pd.read_csv(maf_file, sep="\t", header=0, dtype=object)
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
    maf["Mutation_Class"] = np.vectorize(lambda x: "Novel" if x is np.nan else "")(
        maf["Status"]
    )

    # add modified cosmic column
    maf["Cosmic_ID"] = np.vectorize(customize_cosmic, otypes=[str])(
        maf["cosmic_ID"], maf["cosmic_OCCURENCE"]
    )

    #
    try:
        maf = maf[MAF_COLUMNS_SELECT]
    except KeyError:
        missing_columns = set(MAF_COLUMNS_SELECT) - set(maf.columns.values.tolist())
        raise Exception(
            "Following required columns are missing in the {}: {}".format(
                maf_file, ",".join(missing_columns)
            )
        )

    # format cDNA, AA, exon columns
    maf["EXON"] = np.vectorize(get_exon, otypes=[str])(
        maf["EXON"], maf["INTRON"], maf["HGVSc"], maf["Variant_Classification"]
    )
    maf = maf.drop(["INTRON"], axis=1)
    maf["HGVSc"] = maf["HGVSc"].apply(lambda x: "" if pd.isnull(x) else x)
    maf["HGVSp_Short"] = maf["HGVSp_Short"].apply(lambda x: "" if pd.isnull(x) else x)

    # Compute columns
    # get max of gnomad
    maf["gnomAD_Max_AF"] = np.nanmax(maf[GNOMAD_COLUMNS].values, axis=1)

    # compute various mutation depth and vaf metrics
    maf["D_t_count_fragment"] = maf["D_t_ref_count_fragment"].astype(int) + maf[
        "D_t_alt_count_fragment"
    ].astype(int)
    maf["SD_t_count_fragment"] = maf["SD_t_ref_count_fragment"].astype(int) + maf[
        "SD_t_alt_count_fragment"
    ].astype(int)
    maf["S_t_ref_count_fragment"] = maf["SD_t_ref_count_fragment"].astype(int) - maf[
        "D_t_ref_count_fragment"
    ].astype(int)
    maf["S_t_alt_count_fragment"] = maf["SD_t_alt_count_fragment"].astype(int) - maf[
        "D_t_alt_count_fragment"
    ].astype(int)
    maf["S_t_count_fragment"] = maf["S_t_ref_count_fragment"].astype(int) + maf[
        "S_t_alt_count_fragment"
    ].astype(int)
    maf["n_count_fragment"] = maf["n_ref_count_fragment"].astype(float) + maf[
        "n_alt_count_fragment"
    ].astype(float)
    maf["S_t_vaf_fragment"] = (
        maf["S_t_alt_count_fragment"].astype(float)
        / maf["S_t_count_fragment"].astype(float)
    ).fillna(0)
    maf["SD_t_vaf_fragment_over_n_vaf_fragment"] = (
        maf["SD_t_vaf_fragment"].astype(float) / maf["n_vaf_fragment"].astype(float)
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

    def reformat_tx(txID, tx_df):
        """
        helper function to get reportable txID
        """
        return tx_df[tx_df.isoform == txID].refseq_id.values.tolist().pop()

    # Get transcript list from the user provided file
    try:
        tx = pd.read_csv(
            ref_tx_file,
            header=0,
            sep="\t",
            usecols=["isoform", "gene_name", "refseq_id"],
            dtype=object,
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

    # TODO: This dummy columns block is to be removed at some point
    maf = add_dummy_columns(maf, MAF_DUMMY_COLUMNS)

    # Replace nan with "" for categorical columns and with
    # "0" for depth and vaf columns
    maf = maf.fillna(
        {
            "D_t_count_fragment": "0",
            "D_t_ref_count_fragment": "0",
            "D_t_alt_count_fragment": "0",
            "D_t_vaf_fragment": "0",
            "S_t_count_fragment": "0",
            "S_t_ref_count_fragment": "0",
            "S_t_alt_count_fragment": "0",
            "S_t_vaf_fragment": "0",
            "SD_t_count_fragment": "0",
            "SD_t_ref_count_fragment": "0",
            "SD_t_alt_count_fragment": "0",
            "SD_t_vaf_fragment": "0",
            "n_count_fragment": "0",
            "n_ref_count_fragment": "0",
            "n_alt_count_fragment": "0",
            "n_vaf_fragment": "0",
        }
    ).fillna("")

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
            if pd.isnull(variant.Status) or not isinstance(variant.Status, str):
                mutation_status_filter = True
            else:
                mutation_status_filter = MUTATION_STATUS_BASED_FILTER(
                    variant.Tumor_Sample_Barcode,
                    variant.Status,
                    variant.D_t_alt_count_fragment,
                    variant.SD_t_alt_count_fragment,
                )
            # set flag to classify if a variant is exonic
            is_exonic = IS_EXONIC_CLASS(
                variant.Hugo_Symbol, variant.Variant_Classification, variant.VCF_POS
            )
            # gene based filtering for ACCESS-Solid vs. ACCESS liquid-plex
            gene_based_filter = GENE_BASED_FILTER(
                variant.Tumor_Sample_Barcode, variant.Hugo_Symbol
            )
            # classify non-panel and non-canonical variants to filtered and dropped files
            if variant.Transcript_ID not in tx_list:
                if mutation_status_filter and gene_based_filter and is_exonic:
                    nef.write(format_var(variant))
                elif is_exonic:
                    ned.write(format_var(variant))
                elif mutation_status_filter and gene_based_filter:
                    nsf.write(format_var(variant))
                else:
                    nsd.write(format_var(variant))
            # exonic variants
            elif is_exonic:
                variant_tuple = is_exonic
                variant = variant._replace(
                    Hugo_Symbol=variant_tuple[0],  # Gene
                    Variant_Classification=variant_tuple[1],  # VariantClass
                    VCF_POS=variant_tuple[2],  # Start coordinate
                    Transcript_ID=reformat_tx(
                        variant.Transcript_ID, tx
                    ),  # TranscriptID
                )
                if mutation_status_filter and gene_based_filter:
                    ef.write(format_var(variant))
                else:
                    ed.write(format_var(variant))
            # silent variants
            else:
                variant = variant._replace(
                    Transcript_ID=reformat_tx(variant.Transcript_ID, tx)
                )
                if mutation_status_filter and gene_based_filter:
                    sf.write(format_var(variant))
                else:
                    sd.write(format_var(variant))


def get_project(titlefile):
    """
    get project name form title file
    """
    try:
        title_file = pd.read_csv(
            titlefile, sep="\t", header=0, usecols=["Sample", "Pool"], dtype=object
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
