#!/usr/bin/env python

import os
import sys
import argparse
import pandas as pd

from python_tools.util import extract_sample_id_from_bam_path


def make_traceback_map(genotyping_bams, title_file, traceback_bam_inputs):
    """
    create a df with all required values for traceback function
    """

    def bam_type(bam):
        """
        helper function to derive bam type from the basename of bam file
        """
        if "simplex" in os.path.basename(bam):
            return "SIMPLEX"
        elif "duplex" in os.path.basename(bam):
            return "DUPLEX"
        else:
            return "STANDARD"

    title_file_df = pd.read_csv(title_file, sep="\t", header="infer")
    project_name = title_file_df["Pool"].unique().values.tolist().pop()
    tumor_sample_ids = title_file_df["Sample"].values.tolist()
    patient_ids = title_file_df["Patient_ID"].values.tolist()
    bam_paths = []
    bam_types = []
    bam_sample_ids = []
    bam_patient_ids = []
    for bam in genotyping_bams:
        bam_sample_id = extract_sample_id_from_bam_path(bam)
        if bam_sample_id in tumor_sample_ids:
            bam_paths.append(bam)
            bam_types.append(bam_type(bam))
            bam_sample_ids.append(bam_sample_id)
            bam_patient_ids.append(
                dict(zip(tumor_sample_ids, patient_ids))[bam_sample_id]
            )
    project_name_list = [project_name] * len(bam_paths)

    traceback_bam = pd.read_csv(traceback_bam_inputs, header="infer", sep="\t")
    bam_paths.extend(traceback_bam["BAM_file_path"].values.tolist())
    bam_patient_ids.extend(traceback_bam["MRN"].values.tolist())
    bam_sample_ids.extend(traceback_bam["Sample"].values.tolist())
    project_name_list.extend(traceback_bam["Run"].values.tolist())
    bam_types.extend(["STANDARD"] * int(traceback_bam.shape[0]))

    genotyping_ids = [
        "_".join([bam, bamtype])
        for bam, bamtype in dict(zip(bam_sample_ids, bam_types)).iteritems()
    ]

    traceback_map = pd.DataFrame(
        data={
            "Project": project_name_list,
            "Sample": bam_sample_ids,
            "Patient_ID": bam_patient_ids,  # this is the common id for
            "Genotyping_ID": genotyping_ids,
            "BAM": bam_paths,
        }
    )
    return traceback_map


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
        TI_df["T_AltCount"] = TI_df["T_Count"] - TI_df["T_RefCount"]
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
            [
                "Gene",
                "Chromosome",
                "Start_Position",
                "End_Position",
                "Reference_Allele",
                "Tumor_Seq_Allele1",
                "Tumor_Seq_Allele2",
                "Sample",
                "NormalUsed",
                "T_RefCount",  # For prior ACCESS samples, this should reflect SD_T_RefCount
                "T_AltCount",  # For prior ACCESS samples, this should reflect SD_T_AltCount
                "N_RefCount",
                "N_AltCount",
                "VariantClass",
                "Start_Pos",
                "Ref_Allele",
                "Alt_Allele",
            ]
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
                "Start_Pos": "VCF_POS",
                "Ref_Allele": "VCF_REF",
                "Alt_Allele": "VCF_ALT",
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
            "SD_T_RefCount",
            "SD_T_AltCount",
            "N_RefCount",
            "N_AltCount",
            "VariantClass",
            "Start",
            "Ref",
            "Alt",
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
            "SD_T_RefCount": "t_ref_count",
            "SD_T_AltCount": "t_alt_count",
            # "T_RefCount": "t_ref_count",
            # "T_AltCount": "t_alt_count",
            "N_RefCount": "n_ref_count",
            "N_AltCount": "n_alt_count",
            "VariantClass": "Variant_Classification",
            "Start": "VCF_POS",
            "Ref": "VCF_REF",
            "Alt": "VCF_ALT",
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
    make_traceback_map(
        args.tumor_duplex_bams + args.tumor_simplex_bams,
        args.title_file,
        traceback_bam_inputs,
    )


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

