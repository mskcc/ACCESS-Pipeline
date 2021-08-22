#!/usr/bin/env python
import os
import re
import sys
import shutil
import argparse
import pandas as pd
import numpy as np

from python_tools.constants import GENE_BASED_FILTER


def integrate_genotypes(args):
    tbi_maf = pd.read_csv(
        args.traceback_inputs_maf, sep="\t", header="infer", dtype=str
    )
    tbo_maf = pd.read_csv(args.traceback_out_maf, header="infer", sep="\t", dtype=str)
    title_file_df = pd.read_csv(args.title_file, sep="\t", header="infer", dtype=str)

    # df of sample identifiers for samples in current project
    sample_identifiers = title_file_df[
        ["Pool", "Sample", "AccessionID", "Patient_ID"]
    ].rename(
        index=str,
        columns={
            "Pool": "Run",
            "Sample": "Sample",
            "AccessionID": "Accession",
            "Patient_ID": "MRN",
        },
    )
    # allow only one unique projectID
    projectIDs = set(sample_identifiers["Run"].values.tolist())
    if len(projectIDs) > 1:
        raise Exception("Multiple Pool/Project IDs detected in the title file.")
    else:
        current_project = projectIDs.pop()

    # add samples identifiers for samples from previous projects
    sample_identifiers_from_tb = (
        tbi_maf[["Run", "Tumor_Sample_Barcode", "Accession", "MRN"]]
        .rename(index=str, columns={"Tumor_Sample_Barcode": "Sample"})
        .drop_duplicates()
    )

    sample_identifiers = pd.concat(
        [sample_identifiers, sample_identifiers_from_tb]
    ).drop_duplicates()

    # control samples from current project that should be skipped in genotyping
    control_samples = title_file_df[title_file_df["Class"].str.contains("Pool")][
        "Sample"
    ].values.tolist()

    # create a new column of sample name without DUPLEX/SIMPLEX/STANDARD identifiers
    tbo_maf["Tumor_Sample_Barcode_simplified"] = tbo_maf[
        "Tumor_Sample_Barcode"
    ].replace(to_replace="_STANDARD$|_SIMPLEX$|_DUPLEX$", value="", regex=True)

    # get unique identifier based on Tumor_Sample_Barcode_simplified
    tbo_maf = pd.merge(
        tbo_maf,
        sample_identifiers[["Run", "Sample", "MRN", "Accession"]],
        left_on=["Tumor_Sample_Barcode_simplified"],
        right_on=["Sample"],
    ).drop(["Sample"], axis=1)

    # Merge gbcm input and output (genotyped) maf based on genomic coordinates and sampleID
    tbf = pd.merge(
        tbo_maf,
        tbi_maf,
        how="left",
        left_on=[
            "Chromosome",
            "Start_Position",
            "End_Position",
            "Reference_Allele",
            "Tumor_Seq_Allele2",
            "MRN",
        ],
        right_on=[
            "Chromosome",
            "Start_Position",
            "End_Position",
            "Reference_Allele",
            "Tumor_Seq_Allele2",
            "MRN",
        ],
    )

    # gbcm is a scatter tool. Therefore, for each sample, drop mutations
    #  that did not originate from itself or from a related sample.
    tbf = tbf.drop(tbf[tbf["Tumor_Sample_Barcode_y"].isnull()].index)

    # select required columns and drop duplicates
    tbf = tbf[
        [
            "Hugo_Symbol_x",
            "VCF_POS",
            "VCF_REF",
            "VCF_ALT",
            "t_total_count_fragment",
            "t_ref_count_fragment",
            "t_alt_count_fragment",
            "Tumor_Sample_Barcode_x",
            "Tumor_Sample_Barcode_simplified",
            "Chromosome",
            "Run_x",
            "Accession_x",
            "MRN",
        ]
    ].drop_duplicates()

    tbf["t_vaf_fragment"] = tbf["t_alt_count_fragment"].apply(float) / (
        tbf["t_alt_count_fragment"].apply(float)
        + tbf["t_ref_count_fragment"].apply(float)
    )

    # remove genotyped variants that do not match positions
    # TODO: why is this happening? GBCM?
    tbf[tbf["VCF_POS"].isnull()].to_csv(
        os.path.join(args.outdir, "traceback_orphan_data.txt"),
        header=True,
        index=None,
        sep="\t",
    )
    tbf = tbf[tbf["VCF_POS"].notnull()]
    tbf["t_vaf_fragment"].replace([np.inf, np.nan, -np.inf], 0.0, inplace=True)

    # Select columns for final reporting
    tbf = tbf[
        [
            "Run_x",
            "MRN",
            "Tumor_Sample_Barcode_x",
            "Accession_x",
            "Chromosome",
            "VCF_POS",
            "VCF_REF",
            "VCF_ALT",
            "t_total_count_fragment",
            "t_ref_count_fragment",
            "t_alt_count_fragment",
            "t_vaf_fragment",
        ]
    ].rename(
        index=str,
        columns={
            "Run_x": "#Run",
            "MRN": "MRN",
            "Tumor_Sample_Barcode_x": "Sample",
            "Accession_x": "Accession",
            "Chromosome": "Chr",
            "VCF_POS": "Pos",
            "VCF_REF": "Ref",
            "VCF_ALT": "Alt",
            "t_total_count_fragment": "DP",
            "t_ref_count_fragment": "RD",
            "t_alt_count_fragment": "AD",
            "t_vaf_fragment": "VF",
        },
    )

    # set depth and vaf to int and float types
    tbf[["DP", "RD", "AD"]] = tbf[["DP", "RD", "AD"]].apply(lambda x: x.astype(int))
    tbf["VF"] = tbf["VF"].apply(float)

    # Merge and remove bam types from sample id
    tbf_simplex = tbf[tbf["Sample"].str.contains("SIMPLEX")].reset_index(drop=True)
    tbf_duplex = tbf[tbf["Sample"].str.contains("DUPLEX")].reset_index(drop=True)
    tbf_standard = tbf[tbf["Sample"].str.contains("STANDARD")]

    # get simplex-duplex metrics from simplex and duplex
    for metric in ["DP", "RD", "AD"]:
        tbf_duplex[metric] = tbf_duplex[metric] + tbf_simplex[metric]
    tbf_duplex["VF"] = tbf_duplex["AD"].apply(float) / (
        tbf_duplex["AD"].apply(float) + tbf_duplex["RD"].apply(float)
    )
    tbf_duplex["VF"].replace([np.inf, np.nan, -np.inf], 0.0, inplace=True)

    # combined standard bam and simplex-duplex metrics for final traceback
    tbf = pd.concat([tbf_standard, tbf_duplex], ignore_index=True)

    # label exonic and silent mutations as "Genotyped" if present in
    #  tbf and passes threshold.
    intersect_variants(
        args.exonic_filtered,
        args.exonic_dropped,
        tbi_maf,
        sample_identifiers,
        control_samples,
        current_project,
    )
    intersect_variants(
        args.silent_filtered,
        args.silent_dropped,
        tbi_maf,
        sample_identifiers,
        control_samples,
        current_project,
    )

    # prepare all variants for final traceback output
    tbf["Sample"] = tbf["Sample"].replace(
        to_replace="_STANDARD$|_DUPLEX$", value="", regex=True
    )

    # Add dummy columns to satisfy cvr requirements.
    for index in ["RDP", "RDN", "ADP", "ADN", "SB"]:
        tbf[index] = ""

    # print traceback multi-line header
    with open(os.path.join(args.outdir, "traceback.txt"), "w") as tf:
        tf.write(traceback_header())

    # print traceback data
    tbf.to_csv(
        os.path.join(args.outdir, "traceback.txt"),
        header=True,
        sep="\t",
        index=False,
        mode="a",
    )


def intersect_variants(filtered, dropped, tbi_maf, sample_metadata, control_samples=[], poolID = ""):
    """
    parse genotyped data and re-classify filtered and dropped variants.
    """
    df_from_each_file = (
        pd.read_csv(
            f, index_col=None, header=0, sep="\t", keep_default_na=False, dtype=str
        )
        for f in [filtered, dropped]
    )
    # convert all all variant to maf and concat into a single df
    variants = pd.concat(df_from_each_file, ignore_index=True)
    variants["Mutation_Class"] = variants["Mutation_Class"].fillna("")
    filtered_target, dropped_target = map(
        lambda x: re.sub(".pre_traceback.txt$", ".txt", os.path.basename(x)),
        [filtered, dropped],
    )

    # write new filtered and dropped files
    # Ideally this part should be redone using pd.merge instead of iteration for efficiency
    for i, var in enumerate(variants.itertuples()):
        Sample = var.Sample
        if Sample in control_samples:
            continue
        # Get patient id from title file
        Patient_ID = (
            sample_metadata[sample_metadata["Sample"] == Sample]["MRN"].tolist().pop()
        )
        # select mutatons from traceback input maf file that matches coordinate of 
        #  the current variant and belongs to any sample from this patient excluding 
        #  the ones in the current project.
        select = tbi_maf[
            (tbi_maf["VCF_REF"].values == var.Ref)
            & (tbi_maf["VCF_ALT"].values == var.Alt)
            & (tbi_maf["VCF_POS"].apply(int).values == int(var.Start))
            & (tbi_maf["Tumor_Sample_Barcode"].str.contains(Patient_ID))
            & (~(tbi_maf["Run"].values == poolID))
        ]
        
        # select = tbf[
        #     (tbf["Ref"].values == var.Ref)
        #     & (tbf["Alt"].values == var.Alt)
        #     & (tbf["Pos"].apply(int).values == int(var.Start))
        #     & (tbf["Sample"].str.contains(Patient_ID))
        #     & ~(tbf["Sample"].str.contains(Sample + "_"))
        # ]
        # if the variant is present in any prior IMAPCT sample at VF >= 0.02
        #  or prior ACCESS SIMPLEX-DUPLEX at VF >= 0.001, tag it as genotyped.
        # if (
        #     select[
        #        ~(select["Sample"].str.contains("DUPLEX"))
        #        & (select["VF"].apply(float).values >= 0.02)
        #    ].shape[0]
        #    > 0
        #    or select[
        #        (select["Sample"].str.contains("DUPLEX"))
        #        & (select["VF"].apply(float).values >= 0.001)
        #    ].shape[0]
        #    > 0
        #):

        if select.shape[0] > 0:
            mut_class = ",".join([variants["Mutation_Class"][i], "Genotyped"])
            variants.at[i, "Mutation_Class"] = (
                mut_class[1:] if mut_class.startswith(",") else mut_class
            )
    
    variants[(~(variants["Mutation_Class"] == "")) & (variants[["Sample", "Gene"]].apply(lambda x: GENE_BASED_FILTER(x.Sample, x.Gene), axis=1))].to_csv(
        filtered_target, header=True, index=None, sep="\t", mode="w"
    )
    variants[~((~(variants["Mutation_Class"] == "")) & (variants[["Sample", "Gene"]].apply(lambda x: GENE_BASED_FILTER(x.Sample, x.Gene), axis=1)))].to_csv(
        dropped_target, header=True, index=None, sep="\t", mode="w"
    )


def traceback_header():
    """
    return traceback header.
    """
    header = """##fileformat=Traceback v1.1
##COLUMN=<ID=Run,Type=AlphaNum,Description="Pool/Cohort level identifier">
##COLUMN=<ID=MRN,Type=Integer,Description="Patient identifier">
##COLUMN=<ID=Sample,Type=AlphaNum,Description="Unique sample identifier">
##COLUMN=<ID=Accession,Type=AlphaNum,Description="Unique sample identifier">
##COLUMN=<ID=Chr,Type=AlphaNum,Description="Chromosome">
##COLUMN=<ID=Pos,Type=Integer,Description="Starting genomic coordinate of the variant">
##COLUMN=<ID=Ref,Type=Alpha,Description="Reference base(s)">
##COLUMN=<ID=Alt,Type=Alpha,Description="Variant base(s)">
##COLUMN=<ID=DP,Type=Integer,Description="Total fragment depth">
##COLUMN=<ID=RD,Type=Integer,Description="Reference fragment count">
##COLUMN=<ID=AD,Type=Integer,Description="Variant fragment count">
##COLUMN=<ID=VF,Type=Float,Description="Variant frequency">
##COLUMN=<ID=RDP,Type=Null,Description="Reference depth positive strand">
##COLUMN=<ID=RDN,Type=Null,Description="Reference depth negative strand">
##COLUMN=<ID=ADP,Type=Null,Description="Variant depth positive strand">
##COLUMN=<ID=ADN,Type=Null,Description="Variant depth negative strand">
##COLUMN=<ID=SB,Type=Null,Description="positive-negative strand bias ratio and fisher two-tailed test p-values for strand bias">
"""
    return header


def main():
    """
    Parse arguments

    :return:
    """
    parser = argparse.ArgumentParser(
        prog="traceback_inputs.py", description="FILL", usage="%(prog)s [options]"
    )
    parser.add_argument(
        "-t",
        "--title_file",
        action="store",
        dest="title_file",
        required=False,
        help="Title file",
    )
    parser.add_argument(
        "-ef",
        "--exonic_filtered",
        action="store",
        dest="exonic_filtered",
        required=True,
        help="Path to exonic filtered mutations file",
    )
    parser.add_argument(
        "-sf",
        "--silent_filtered",
        action="store",
        dest="silent_filtered",
        required=True,
        help="Path to silent filtered mutations file",
    )
    parser.add_argument(
        "-ed",
        "--exonic_dropped",
        action="store",
        dest="exonic_dropped",
        required=True,
        help="Path to exonic dropped mutations file",
    )
    parser.add_argument(
        "-sd",
        "--silent_dropped",
        action="store",
        dest="silent_dropped",
        required=True,
        help="Path to silent dropped mutations file",
    )
    parser.add_argument(
        "-tim",
        "--traceback_inputs_maf",
        action="store",
        dest="traceback_inputs_maf",
        required=True,
        help="Path to traceback inputs maf file",
    )
    parser.add_argument(
        "-tom",
        "--traceback_out_maf",
        action="store",
        dest="traceback_out_maf",
        required=True,
        help="Path to genotyped traceback output maf file",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        action="store",
        dest="outdir",
        required=False,
        default=os.getcwd(),
        help="Output directory",
    )
    args = parser.parse_args()
    integrate_genotypes(args)


if __name__ == "__main__":
    main()
