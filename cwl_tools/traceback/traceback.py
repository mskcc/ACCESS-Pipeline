#!/usr/bin/env python

import os
import sys
import argparse
import pandas as pd


def group_mutations_maf(title_file, TI_mutations, mutation_file_list):
    """
    Main function
    """

    def vcf_to_maf_coord(Start, Ref, Alt):
        if len(Ref) == len(Alt):
            return (Start, Start, Ref, Alt)
        elif len(Ref) > len(Alt):
            if Ref[0] == Alt[0]:
                return (
                    str(int(Start) + 1),
                    str(int(Start) + len(Alt)),
                    Ref[1:],
                    ("-" if len(Alt) == 1 else Alt[1:]),
                )
            else:
                return (Start, Start, Ref, Alt)
        elif len(Ref) < len(Alt):
            if Ref[0] == Alt[0]:
                return (
                    str(int(Start) + 1),
                    str(int(Start) + len(Ref)),
                    ("-" if len(Ref) == 1 else Ref[1:]),
                    Alt[1:],
                )
            else:
                return (Start, Start, Ref, Alt)

    def variant_type(Ref, Alt):
        if len(Ref) > len(Alt):
            return "DEL"
        elif len(Ref) < len(Alt):
            return "INS"
        else:
            return "SNV"

    def TI_mutations_to_maf(TI_mutations):
        TI_df = pd.read_csv(TI_mutations, sep="\t", header="infer")
        TI_df[
            ["Start_Position", "End_Position", "Reference_Allele", "Tumor_Seq_Allele2"]
        ] = pd.DataFrame(
            TI_df.apply(
                lambda x: vcf_to_maf_coord(
                    x["Start_Pos"], x["Ref_Allele"], x["Alt_Allele"]
                ),
                axis=1,
            ).values.tolist()
        )
        TI_df["Tumor_Seq_Allele1"] = TI_df["Reference_Allele"]
        for col in [
            "VariantClass",
            "Gene",
            "NormalUsed",
            "T_RefCount",  # SD_T_RefCount",
            "T_AltCount",  # SD_T_AltCount",
            "N_RefCount",
            "N_AltCount",
        ]:
            if col not in TI_df.columns:
                TI_df[col] = ""

        TI_df = TI_df[
            "Gene",
            "Chromosome",
            "Start_Position",
            "End_Position",
            "Reference_Allele",
            "Tumor_Seq_Allele1",
            "Tumor_Seq_Allele2",
            "Sample",
            "NormalUsed",
            "T_RefCount",  # SD_T_RefCount",
            "T_AltCount",  # SD_T_AltCount",
            "N_RefCount",
            "N_AltCount",
            "VariantClass",
        ].rename(
            index=str,
            columns={
                "Gene": "Hugo_Symbol",
                "Chromosome": "Chromosome",
                "Start_Position": "Start_Position",
                "End_Position": "End_Position",
                "Reference_Allele": "Reference_Allele",
                "Tumor_Seq_Allele1": "Tumor_Seq_Allele1",
                "Tumor_Seq_Allele2": "Tumor_Seq_Allele2",
                "Sample": "Tumor_Sample_Barcode",
                "NormalUsed": "Matched_Norm_Sample_Barcode",
                # "SD_T_RefCount": "t_ref_count",
                # "SD_T_AltCount": "t_alt_count",
                "T_RefCount": "t_ref_count",
                "T_AltCount": "t_alt_count",
                "N_RefCount": "n_ref_count",
                "N_AltCount": "n_alt_count",
                "VariantClass": "Variant_Classification",
            },
        )
        return TI_df

    mutation_file_list = mutation_file_list.split(",")
    df_from_each_file = (
        pd.read_csv(f, index_col=None, header=0, sep="\t") for f in mutation_file_list
    )
    concat_df = pd.concat(df_from_each_file, ignore_index=True)
    concat_df[
        ["Start_Position", "End_Position", "Reference_Allele", "Tumor_Seq_Allele2"]
    ] = pd.DataFrame(
        concat_df.apply(
            lambda x: vcf_to_maf_coord(x["Start"], x["Ref"], x["Alt"]), axis=1
        ).values.tolist()
    )
    concat_df["Variant_Type"] = concat_df.apply(
        lambda x: variant_type(x["Ref"], x["Alt"]), axis=1
    )
    concat_df["Tumor_Seq_Allele1"] = concat_df["Reference_Allele"]
    concat_df = concat_df[
        [
            "Gene",
            "Chrom",
            "Start_Position",
            "End_Position",
            "Reference_Allele",
            "Tumor_Seq_Allele1",
            "Tumor_Seq_Allele2",
            "Sample",
            "NormalUsed",
            "T_RefCount",  # SD_T_RefCount",
            "T_AltCount",  # SD_T_AltCount",
            "N_RefCount",
            "N_AltCount",
            "VariantClass",
        ]
    ]
    concat_df = concat_df.rename(
        index=str,
        columns={
            "Gene": "Hugo_Symbol",
            "Chrom": "Chromosome",
            "Start_Position": "Start_Position",
            "End_Position": "End_Position",
            "Reference_Allele": "Reference_Allele",
            "Tumor_Seq_Allele1": "Tumor_Seq_Allele1",
            "Tumor_Seq_Allele2": "Tumor_Seq_Allele2",
            "Sample": "Tumor_Sample_Barcode",
            "NormalUsed": "Matched_Norm_Sample_Barcode",
            # "SD_T_RefCount": "t_ref_count",
            # "SD_T_AltCount": "t_alt_count",
            "T_RefCount": "t_ref_count",
            "T_AltCount": "t_alt_count",
            "N_RefCount": "n_ref_count",
            "N_AltCount": "n_alt_count",
            "VariantClass": "Variant_Classification",
        },
    )
    if TI_mutations:
        concat_df = pd.concat([concat_df, TI_mutations_to_maf(TI_mutations)])
    concat_df.to_csv(
        "traceback_inputs.maf", header=True, index=None, sep="\t", mode="w"
    )
    return


def main():
    """
    Parse arguments

    :return:
    """
    parser = argparse.ArgumentParser(
        prog="traceback.py", description="FILL", usage="%(prog)s [options]"
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
        "-tm",
        "--ti_mutations",
        action="store",
        dest="ti_mutations",
        required=False,
        help="Input txt file of tumor informed mutations",
    )
    parser.add_argument(
        "-ml",
        "--mutation_list",
        action="store",
        dest="mutation_list",
        required=True,
        help="List of mutation files from the current project",
    )
    args = parser.parse_args()
    group_mutations_maf(args.title_file, args.ti_mutations, args.mutation_list)


if __name__ == "__main__":
    main()


#     maf_df = pd.read_csv(maf, header="infer", sep="\t", skiprows=1)
#     mad_df = maf_df[MAF_HEADER]

#     for mut_file in mutations_file_list:

#     title_file_df = pd.read_csv(title_file, header="infer", sep="\t")
#     mutations = pd.read_csv(mutation_list, header="infer", sep="\t")
#     bams = pd.read_csv(bam_list, header="infer", sep="\t")
#     unique_samples = list(
#         set(
#             title_file_df["MRN"].values.tolist(),
#             mutations["MRN"].values.tolist(),
#             bams["MRN"].values.tolist(),
#         )
#     )
#     for samples in unique_samples:
#         make_vcf


# def variants_to_vcf(group, project_name, variant_file):
#     vcf_list = []
#     variants = pd.read_csv(variant_file, header="infer")
#     variants = variants["Sample", "MRN", "Chrom", "Start", "Ref", "Alt"]
#     for sample in variants["Sample"].values.tolist().unique():
#         with open(sample + "_traceback_input.vcf", "w") as f:
#             f.write(TRACEBACK_INPUT_VCF_HEADER + "\n")
#         sample_vcf = variants[variants["Sample"] == sample]
#         sample_vcf.to_csv(
#             sample + "_traceback_input.vcf",
#             header=False,
#             index=None,
#             sep="\t",
#             mode="a",
#         )
#         vcf_list.append(sample + "_traceback_input.vcf")
#     return vcf_list

