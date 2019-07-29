#!/usr/bin/env python
import os
import sys
import pandas as pd

def main(tbi_f, tbo_f, vf, of):
    tbi_maf = pd.read_csv(tbi_f, sep="\t", header="infer", dtype=object)
    tbo_maf = pd.read_csv(tbo_f, header="infer", sep="\t", dtype=object)

    tbf = pd.merge(tbo_maf, tbi_maf, how="left", left_on=["Chromosome", "Start_Position", "End_Position", "Reference_Allele", "Tumor_Seq_Allele1"], right_on=["Chromosome", "Start_Position", "End_Position", "Reference_Allele", "Tumor_Seq_Allele2"])

    tbf = tbf[["Hugo_Symbol_x", 'VCF_POS', 'VCF_REF', 'VCF_ALT', 't_ref_count_fragment', 't_alt_count_fragment',  'Tumor_Sample_Barcode_x', 'Chromosome']]

    tbf['t_vaf_fragment'] = tbf['t_alt_count_fragment'].apply(float)/(tbf['t_alt_count_fragment'].apply(float) + tbf['t_ref_count_fragment'].apply(float))

    variants = pd.read_csv(vf, header="infer", sep="\t")

    for i, var in enumerate(variants.itertuples()):
        Sample = var.Sample
        Patient_ID = Sample.split("-")[0]
        select = tbf[(tbf['VCF_REF'].values == var.Ref) & (tbf['VCF_ALT'].values == var.Alt) & (tbf['VCF_POS'].apply(int).values == int(var.Start)) & (tbf['t_vaf_fragment'].apply(float).values >= 0.02)]
        select = select[~(select["Tumor_Sample_Barcode_x"].str.contains("DUPLEX")) & ~(select["Tumor_Sample_Barcode_x"].str.contains("SIMPLEX"))]
        select = select[select['Tumor_Sample_Barcode_x'].str.contains(Patient_ID)]
        if select.shape[0] > 0:
            variants.at[i, 'Mutation_Class'] = ",".join([variants["Mutation_Class"][i], "Genotyped"])
    variants.to_csv(of, header=True, index=None, sep="\t", mode="w")

if __name__ == "__main__":
    tbi_f = sys.argv[1]
    tbo_f = sys.argv[2]
    vf = sys.argv[3]
    of = sys.argv[4]
    main(tbi_f, tbo_f, vf, of)
