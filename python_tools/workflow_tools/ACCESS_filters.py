# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 18:10:40 2018

@author: hasanm
"""

import argparse
import os.path
import pandas as pd
import numpy as np

np.seterr(divide='ignore', invalid='ignore')

mutation_key = ['Chromosome', 'Start_Position','End_Position','Reference_Allele','Tumor_Seq_Allele2']


def convert_annomaf_to_df(arg):
    if os.path.isfile(arg.anno_maf):
        annotation_file = arg.anno_maf
        df_annotation = pd.read_csv(annotation_file,sep='\t', header=0)
        df_annotation['Chromosome'] = df_annotation['Chromosome'].astype(str)
        df_annotation.set_index(mutation_key, drop=False, inplace=True)
        df_annotation.rename(columns ={'Matched_Norm_Sample_Barcode':'caller_Norm_Sample_Barcode','t_depth':'caller_t_depth', 't_ref_count':'caller_t_ref_count', 't_alt_count':'caller_t_alt_count', 'n_depth':'caller_n_depth', 'n_ref_count':'caller_n_ref_count', 'n_alt_count':'caller_n_alt_count'}, inplace=True)
        return df_annotation
    else:
        raise Exception('The path to the annotation MAF file does not exist')
    
def convert_fillout_to_df(args):
    '''extract and stanardize a fillout file'''
    if os.path.isfile(args.fillout_maf):
        fillout_file = args.fillout_maf
        df_full_fillout = pd.read_csv(fillout_file, sep='\t', header=0)
        df_full_fillout['Chromosome'] = df_full_fillout['Chromosome'].astype(str)
        df_full_fillout.drop('Tumor_Seq_Allele2', axis=1, inplace=True)
        df_full_fillout.rename(columns = {'Tumor_Seq_Allele1':'Tumor_Seq_Allele2'}, inplace=True)
        df_full_fillout.set_index(mutation_key, drop=False, inplace=True)
        return df_full_fillout
    else:
        raise Exception('The path to the annotation MAF file does not exist')


def extract_fillout_type(df_full_fillout):
    def find_VAFandsummary(df_fillout): 
        df_fillout = df_fillout.copy()
        #find the VAF from the fillout
        df_fillout['t_vaf_fragment'] = (df_fillout['t_alt_count_fragment'] / (df_fillout['t_alt_count_fragment'].astype(int) + df_fillout['t_ref_count_fragment'].astype(int))).round(4)
        df_fillout['summary_fragment'] = 'DP='+(df_fillout['t_alt_count_fragment'].astype(int) + df_fillout['t_ref_count_fragment'].astype(int)).astype(str)+';RD='+  df_fillout['t_ref_count_fragment'].astype(str)+';AD='+ df_fillout['t_alt_count_fragment'].astype(str)+';VF='+df_fillout['t_vaf_fragment'].fillna(0).astype(str)
        return df_fillout
        
    def create_duplexsimplex(df_s, df_d):
        df_s = df_s.copy()
        df_d = df_d.copy()
        #Prep Simplex
        df_s.rename(columns = {'t_alt_count_fragment': 't_alt_count_fragment_simplex','t_ref_count_fragment':'t_ref_count_fragment_simplex'}, inplace=True)   
        df_s['Tumor_Sample_Barcode'] = df_s['Tumor_Sample_Barcode'].str.replace('-SIMPLEX','')
        df_s.set_index('Tumor_Sample_Barcode', append=True, drop=False, inplace=True)
        #Prep Duplex
        df_d.rename(columns = {'t_alt_count_fragment': 't_alt_count_fragment_duplex','t_ref_count_fragment':'t_ref_count_fragment_duplex'}, inplace=True)        
        df_d.set_index('Tumor_Sample_Barcode', append=True, drop=False, inplace=True)
        #Merge
        df_ds = df_s.merge(df_d[['t_ref_count_fragment_duplex','t_alt_count_fragment_duplex']], left_index=True, right_index=True)
        ##Add
        df_ds['t_ref_count_fragment'] = df_ds['t_ref_count_fragment_simplex'] + df_ds['t_ref_count_fragment_duplex']
        df_ds['t_alt_count_fragment'] = df_ds['t_alt_count_fragment_simplex'] + df_ds['t_alt_count_fragment_duplex']
        df_ds['t_total_count_fragment'] = df_ds['t_alt_count_fragment'] + df_ds['t_ref_count_fragment']
        ##clean up
        fillout_type = df_ds['Fillout-Type']+'-DUPLEX'
        df_ds.drop(['Fillout-Type', 't_ref_count_fragment_simplex', 't_ref_count_fragment_duplex', 't_alt_count_fragment_simplex','t_alt_count_fragment_duplex'], axis=1, inplace=True)
        df_ds['Fillout-Type'] = fillout_type
        df_ds['Tumor_Sample_Barcode'] = df_ds['Tumor_Sample_Barcode']+'-SIMPLEX-DUPLEX'
        df_ds.set_index(mutation_key, drop=False, inplace=True)
        df_ds = find_VAFandsummary(df_ds)
        return df_ds

    #tag fillout type in full fillout
    df_full_fillout['Fillout-Type'] = df_full_fillout['Tumor_Sample_Barcode'].apply(lambda x: "CURATED-SIMPLEX" if "-CURATED-SIMPLEX" in x else ("SIMPLEX" if "-SIMPLEX" in x else ("CURATED" if "CURATED" in x else "POOL")))
    #extract curated duplex and and VAf and summary column
    df_curated = (df_full_fillout.loc[df_full_fillout['Fillout-Type'] == 'CURATED'])
    df_curated = find_VAFandsummary(df_curated)
    #extract simplex and transform to simplex +duplex
    df_curatedsimplex = (df_full_fillout.loc[df_full_fillout['Fillout-Type'] == 'CURATED-SIMPLEX'])
    df_ds_curated = create_duplexsimplex(df_curatedsimplex, df_curated)
    #extract duplex and and VAf and summary column
    df_pool = (df_full_fillout.loc[df_full_fillout['Fillout-Type'] == 'POOL'])
    df_pool = find_VAFandsummary(df_pool)
    #extract simplex and transform to simplex +duplex
    df_simplex = (df_full_fillout.loc[df_full_fillout['Fillout-Type'] == 'SIMPLEX'])
    df_ds_tumor = create_duplexsimplex(df_simplex, df_pool)
    return df_pool, df_ds_tumor, df_curated, df_ds_curated
  
   
def create_fillout_summary(df_fillout, alt_thres):
    try:
        fillout_type = df_fillout['Fillout-Type'].iloc[0]
        if fillout_type != '':
            fillout_type = fillout_type+'_'
    except:
        print("The fillout provided to summarize was not run through extract_fillout_type")
        fillout_type = ''
        
    # Make the dataframe with the fragment count summary of all the samples per mutation
    summary_table = df_fillout.pivot_table(index=mutation_key, columns='Tumor_Sample_Barcode', values='summary_fragment', aggfunc=lambda x: ' '.join(x))

    # Find the median VAF for the set
    # Todo: handle case where t_vaf_fragment contains numpy.nan
    summary_table[fillout_type + 'median_VAF'] = df_fillout.groupby(mutation_key)['t_vaf_fragment'].median()

    # Find the number of samples with alt count above the threshold (alt_thres)
    summary_table[fillout_type + 'n_fillout_sample_alt_detect'] = df_fillout.groupby(mutation_key)['t_alt_count_fragment'].aggregate(lambda x :(x>alt_thres).sum())

    # Find the number of sample with the Total Depth is >0
    # 't_vaf_fragment' column is NA for samples where mutation had no coverage, so count() will exclude it
    summary_table[fillout_type + 'n_fillout_sample'] = df_fillout.groupby(mutation_key)['t_vaf_fragment'].count()
    return summary_table
 

def extract_tn_genotypes(df_pool, df_ds_tumor, t_samplename, n_samplename):
    df_tn_genotype = df_pool[df_pool['Tumor_Sample_Barcode']==t_samplename][['t_alt_count_fragment', 't_ref_count_fragment','t_vaf_fragment']]

    if df_tn_genotype.shape[0] == 0:
        raise Exception('Tumor Sample ID {} not found in maf file'.format(t_samplename))

    df_ds_genotype = df_ds_tumor[df_ds_tumor['Tumor_Sample_Barcode']==t_samplename+'-SIMPLEX-DUPLEX'][['t_alt_count_fragment', 't_ref_count_fragment','t_vaf_fragment']]
    df_ds_genotype.rename(columns = {'t_alt_count_fragment':'DS_t_alt_count_fragment', 't_ref_count_fragment':'DS_t_ref_count_fragment','t_vaf_fragment':'DS_t_vaf_fragment'}, inplace=True)
    df_tn_genotype = df_tn_genotype.merge(df_ds_genotype, left_index=True, right_index=True)
    if n_samplename != '':
        df_n_genotype = df_pool[df_pool['Tumor_Sample_Barcode']==n_samplename][['t_alt_count_fragment', 't_ref_count_fragment','t_vaf_fragment']]
        df_n_genotype.rename(columns = {'t_alt_count_fragment':'n_alt_count_fragment', 't_ref_count_fragment':'n_ref_count_fragment','t_vaf_fragment':'n_vaf_fragment'}, inplace=True)
        df_n_genotype.insert(0, 'Matched_Norm_Sample_Barcode', n_samplename)        
        df_tn_genotype = df_tn_genotype.merge(df_n_genotype, left_index=True, right_index=True)
    return df_tn_genotype


def make_pre_filtered_maf(args):
    
    df_annotation = convert_annomaf_to_df(args)
    df_full_fillout = convert_fillout_to_df(args)
    df_pool, df_ds_tumor, df_curated, df_ds_curated=extract_fillout_type(df_full_fillout)
    
    df_pool_summary = create_fillout_summary (df_pool, args.tumor_detect_alt_thres)
    df_curated_summary = create_fillout_summary (df_curated, args.curated_detect_alt_thres)
    
    df_ds_tumor_summary = create_fillout_summary (df_ds_tumor, args.DS_tumor_detect_alt_thres)
    df_ds_curated_summary = create_fillout_summary (df_ds_curated, args.DS_curated_detect_alt_thres)
    
    df_tn_geno = extract_tn_genotypes(df_pool, df_ds_tumor, args.tumor_samplename, args.normal_samplename)
    df_pre_filter = df_annotation.merge(df_tn_geno, left_index=True, right_index=True).merge(df_pool_summary, left_index=True, right_index=True).merge(df_ds_tumor_summary, left_index=True, right_index=True).merge(df_curated_summary, left_index=True, right_index=True).merge(df_ds_curated_summary, left_index=True, right_index=True)
    return df_pre_filter


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--anno_maf", help="MAF from Remove Variants module that has all the annotations required in the final MAF", required=True)
    parser.add_argument("--fillout_maf", help="Fillout File", required=True)
    parser.add_argument("--tumor_samplename", help="Tumor Samplename, must be the same as in the Fillout", required=True)
    parser.add_argument("--normal_samplename", help="Normal Samplename, must be the same as in the Fillout", required=True)
    
    #Detected thresholds
    parser.add_argument("--tumor_detect_alt_thres", default=2, type=int, help="The Minimum Alt depth required to be considered detected in fillout")
    parser.add_argument("--curated_detect_alt_thres", default=2, type=int, help="The Minimum Alt depth required to be considered detected in fillout")
    parser.add_argument("--DS_tumor_detect_alt_thres", default=2, type=int, help="The Minimum Alt depth required to be considered detected in fillout")
    parser.add_argument("--DS_curated_detect_alt_thres", default=2, type=int, help="The Minimum Alt depth required to be considered detected in fillout")
    
    #Germline Parameters #n_TD_min=20, n_vaf_germline_thres=.4, t_TD_min=20, t_vaf_germline_thres=.4    
    parser.add_argument("--normal_TD_min", default=20, type=int, help="The Minimum Total Depth required in Matched Normal to consider a variant Germline")
    parser.add_argument("--normal_vaf_germline_thres", default=.4, type=float, help="The threshold for variant allele fraction required in Matched Normal to be consider a variant Germline")    
    parser.add_argument("--tumor_TD_min", default=20, type=int, help="The Minimum Total Depth required in tumor to consider a variant Likely Germline")
    parser.add_argument("--tumor_vaf_germline_thres", default=.4, type=float, help="The threshold for variant allele fraction required in Tumor to be consider a variant Likely Germline")    
    
    #Tiering Parameters #tier_one_alt_min=3, tier_two_alt_min=5
    parser.add_argument("--tier_one_alt_min", default=3, type=int, help="The Minimum Alt Depth required in hotspots")
    parser.add_argument("--tier_two_alt_min", default=5, type=int, help="The Minimum Alt Depth required in non-hotspots")
    
    #Occurance in curated  n_fillout_sample_detect_min)
    parser.add_argument("--min_n_curated_samples_alt_detected", default=2, type=int, help="The Minimum number of curated samples variant is detected to be flagged")
    
    #Occurance in curated  n_fillout_sample_detect_min)
    parser.add_argument("--tn_ratio_thres", default=5, type=int, help="Tumor-Normal variant fraction ratio threshold")
    
    args = parser.parse_args()
    return args


def apply_filter_maf (df_pre_filter, args):
    # FILTERS
    def tag_germline(mut, status, args):
        #if there is a matched normal and it has sufficient coverage
        if 'n_vaf_fragment' in mut.index.tolist() and mut['n_ref_count_fragment'] + mut['n_alt_count_fragment'] > args.normal_TD_min:
            if mut['n_vaf_fragment'] > args.normal_vaf_germline_thres:
                status = status + 'Germline;'
        elif 'common_variant' in mut['FILTER'] and mut['t_ref_count_fragment'] + mut['t_alt_count_fragment'] > args.tumor_TD_min and mut['t_vaf_fragment'] > args.tumor_vaf_germline_thres:
            status = status + 'LikelyGermline;'
        return status
    #TODO:TEST        
    def tag_below_alt_threshold(mut, status, args):
        if mut['t_alt_count_fragment'] < args.tier_one_alt_min or (mut['hotspot_whitelist'] == False and mut['t_alt_count_fragment'] < args.tier_two_alt_min):
            if mut['caller_t_alt_count']>= args.tier_one_alt_min or (mut['hotspot_whitelist'] == False and mut['caller_t_alt_count'] >= args.tier_two_alt_min):
                status = status+'LostbyGenotyper;'
            else:
                status = status+'BelowAltThreshold;'
        return status
        # ASK MIKE: add truncated mutaions to below threshold 'Nonsense_Mutation', 'Splice_Site', 'Frame_Shift_Ins', 'Frame_Shift_Del'
        
    def occurence_in_curated (mut, status, args):
        if mut['CURATED_n_fillout_sample_alt_detect'] > args.min_n_curated_samples_alt_detected:
            status = status + 'InCurated;'
        return status
    
    def occurence_in_normal (mut, status, args):
        #if normal and tumor coverage is greater than the minimal
        if mut['t_ref_count_fragment'] + mut['t_alt_count_fragment'] > args.tumor_TD_min:
            if mut['CURATED_median_VAF'] != 0:
                if mut['t_vaf_fragment'] / mut['CURATED_median_VAF'] > args.tn_ratio_thres:
                    status = status + 'TNRatio-curatedmedian;'
            
            if 'n_vaf_fragment' in mut.index.tolist() and mut['hotspot_whitelist'] == False:
                if mut['n_ref_count_fragment'] + mut['n_alt_count_fragment'] > args.normal_TD_min and mut['n_vaf_fragment'] != 0:
                    if mut['t_vaf_fragment'] / mut['n_vaf_fragment'] > args.tn_ratio_thres:
                        status = status + 'TNRatio-matchnorm;'
        return status
    
 #Can eliminate, no longer needed as of 02/2019
    def non_exonic (mut, status):
        keep_exonic = ['Missense_Mutation', 'Nonsense_Mutation', 'Splice_Site', 'Frame_Shift_Ins', 'Frame_Shift_Del', 'In_Frame_Ins', 'In_Frame_Del']

        if mut['Variant_Classification'] in keep_exonic:
            status = status
        elif mut['Variant_Classification'] == 'Intron' and mut['Hugo_Symbol'] == 'MET':
            status = status
        elif mut['Variant_Classification'] == "5'Flank" and mut['Hugo_Symbol'] == 'TERT':
            status = status
        else:
            status = status+'NonExonic;'
        return status

    # RUN
    df_post_filter = df_pre_filter.copy()

    df_post_filter['Status'] = ''
    for i, mut in df_post_filter.iterrows():
        status = ''
        status = tag_germline(mut, status, args)
        status = tag_below_alt_threshold(mut, status, args)
        status = occurence_in_curated(mut, status, args)
        status = occurence_in_normal(mut, status, args)
        #status = non_exonic(mut, status)
        df_post_filter.loc[i, 'Status'] = status

    return df_post_filter


def main():
    args = parse_arguments()

    df_pre_filter = make_pre_filtered_maf(args)
    df_post_filter = apply_filter_maf(df_pre_filter, args)

    output_file_name = os.path.basename(args.fillout_maf).replace('.maf', '_filtered.maf')
    df_post_filter.to_csv(output_file_name, header=True, index=None, sep='\t', mode='a')


if __name__ == '__main__':
    main()
