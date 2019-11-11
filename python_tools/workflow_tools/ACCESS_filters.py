# -*- coding: utf-8 -*-
"""
Created on Tue Dec  4 18:10:40 2018

@author: hasanm
"""

import argparse
import os.path
import pandas as pd
import numpy as np
import re

np.seterr(divide='ignore', invalid='ignore')

mutation_key = ['Chromosome', 'Start_Position','End_Position','Reference_Allele','Tumor_Seq_Allele2']

def extract_blacklist(args):
    header=['Chromosome','Start_Position','End_Position','Reference_Allele','Tumor_Seq_Allele','Annotation']
    if os.path.isfile(args.blacklist_file):
        df_blacklist = pd.read_csv(args.blacklist_file,sep='\t', header=0)        
        if list(df_blacklist.columns.values)!=header:
            raise Exception('Blacklist provided is in the wrong formal, file should have the following in the header (in order):'+', '.join(header))
        else:
            df_blacklist.drop(['Annotation'], axis=1, inplace=True)
            df_blacklist.drop_duplicates(inplace=True)
            blacklist=[str(b[0])+"_"+str(b[1])+"_"+str(b[2])+"_"+str(b[3])+"_"+str(b[4]) for b in df_blacklist.values.tolist()]
            return blacklist
    elif args.blacklist_file=='':
        blacklist =[]
        return blacklist
    else:
        raise IOError('Blacklist file provided does not exist')
        
def convert_annomaf_to_df(args):
    def cleanupMuTectColumns(df_annotation):
        df_annotation.loc[(df_annotation['MUTECT'] == 1) & (df_annotation['CallMethod'] != 'MuTect'),'CallMethod'] = 'VarDict,MuTect'
        df_annotation.drop(['TYPE','FAILURE_REASON','MUTECT'], inplace=True, axis=1)
    
    if os.path.isfile(args.anno_maf):
        annotation_file = args.anno_maf
        df_annotation = pd.read_csv(annotation_file,sep='\t', header=0)
        df_annotation['Chromosome'] = df_annotation['Chromosome'].astype(str)
        df_annotation.set_index(mutation_key, drop=False, inplace=True)
        #TODO: It is recommended to sort multi-Index using "df_annotation.sortlevel(inplace=True)" for performance but not sure of downsteams errors.. need to test
        df_annotation.rename(columns ={'Matched_Norm_Sample_Barcode':'caller_Norm_Sample_Barcode','t_depth':'caller_t_depth', 't_ref_count':'caller_t_ref_count', 't_alt_count':'caller_t_alt_count', 'n_depth':'caller_n_depth', 'n_ref_count':'caller_n_ref_count', 'n_alt_count':'caller_n_alt_count','set':'CallMethod'}, inplace=True)
        cleanupMuTectColumns(df_annotation)
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
        df_d['Tumor_Sample_Barcode'] = df_d['Tumor_Sample_Barcode'].str.replace('-DUPLEX', '')
        df_d.set_index('Tumor_Sample_Barcode', append=True, drop=False, inplace=True)
        #Merge
        df_ds = df_s.merge(df_d[['t_ref_count_fragment_duplex','t_alt_count_fragment_duplex']], left_index=True, right_index=True)
        ##Add
        df_ds['t_ref_count_fragment'] = df_ds['t_ref_count_fragment_simplex'] + df_ds['t_ref_count_fragment_duplex']
        df_ds['t_alt_count_fragment'] = df_ds['t_alt_count_fragment_simplex'] + df_ds['t_alt_count_fragment_duplex']
        df_ds['t_total_count_fragment'] = df_ds['t_alt_count_fragment'] + df_ds['t_ref_count_fragment']
        ##clean up
        fillout_type = df_ds['Fillout_Type']+'-DUPLEX'
        df_ds.drop(['Fillout_Type', 't_ref_count_fragment_simplex', 't_ref_count_fragment_duplex', 't_alt_count_fragment_simplex','t_alt_count_fragment_duplex'], axis=1, inplace=True)
        df_ds['Fillout_Type'] = fillout_type
        df_ds['Tumor_Sample_Barcode'] = df_ds['Tumor_Sample_Barcode']+'-SIMPLEX-DUPLEX'
        df_ds.set_index(mutation_key, drop=False, inplace=True)
        df_ds = find_VAFandsummary(df_ds)
        return df_ds
        
    def separate_normal_and_tumor (df_pool, df_ds_tumor):
        tumor_samples=[f.replace('-SIMPLEX-DUPLEX', '') for f in df_ds_tumor.Tumor_Sample_Barcode.unique().tolist()]
        df_tumor=(df_pool.loc[df_pool['Tumor_Sample_Barcode'].isin(tumor_samples)])
        df_normal=(df_pool.loc[~df_pool['Tumor_Sample_Barcode'].isin(tumor_samples)])
        df_normal.Fillout_Type='NORMAL'
        return df_tumor, df_normal
        
    #tag fillout type in full fillout
    df_full_fillout['Fillout_Type'] = df_full_fillout['Tumor_Sample_Barcode'].apply(lambda x: "CURATED-SIMPLEX" if "-CURATED-SIMPLEX" in x else ("SIMPLEX" if "-SIMPLEX" in x else ("CURATED-DUPLEX" if "CURATED-DUPLEX" in x else "POOL")))
    #extract curated duplex and and VAf and summary column
    df_curated = (df_full_fillout.loc[df_full_fillout['Fillout_Type'] == 'CURATED-DUPLEX'])
    df_curated = find_VAFandsummary(df_curated)
    #extract simplex and transform to simplex +duplex
    df_curatedsimplex = (df_full_fillout.loc[df_full_fillout['Fillout_Type'] == 'CURATED-SIMPLEX'])
    df_ds_curated = create_duplexsimplex(df_curatedsimplex, df_curated)
    #extract duplex and and VAf and summary column
    df_pool = (df_full_fillout.loc[df_full_fillout['Fillout_Type'] == 'POOL'])
    df_pool = find_VAFandsummary(df_pool)
    #extract simplex and transform to simplex +duplex
    df_simplex = (df_full_fillout.loc[df_full_fillout['Fillout_Type'] == 'SIMPLEX'])
    df_ds_tumor = create_duplexsimplex(df_simplex, df_pool)
    #separate tumor samples from Normal samples from POOL Fillout_Type
    #This is done by assuming all tumor samples have a simplex-duplex tumor sample genotyped, while normals do not. Samples not in DS_tumor are assumed to be normals
    df_tumor, df_normal=separate_normal_and_tumor (df_pool, df_ds_tumor)
    return df_tumor, df_normal, df_ds_tumor, df_curated, df_ds_curated
  
   
def create_fillout_summary(df_fillout, alt_thres):
    try:
        fillout_type = df_fillout['Fillout_Type'].iloc[0]
        if fillout_type != '':
            fillout_type = fillout_type+'_'
    except:
        print("The fillout provided to summarize was not run through extract_fillout_type")
        fillout_type = ''
        raise
    
    #Drop columns that are in the index to eliminate error
    df_fillout.drop(mutation_key, inplace=True, axis=1)
    # Make the dataframe with the fragment count summary of all the samples per mutation
    summary_table = df_fillout.pivot_table(index=mutation_key, columns='Tumor_Sample_Barcode', values='summary_fragment', aggfunc=lambda x: ' '.join(x))

    # Find the median VAF for the set
    # Todo: handle case where t_vaf_fragment contains numpy.nan
    summary_table[fillout_type + 'median_VAF'] = df_fillout.groupby(mutation_key)['t_vaf_fragment'].median()

    # Find the number of samples with alt count above the threshold (alt_thres)
    summary_table[fillout_type + 'n_fillout_sample_alt_detect'] = df_fillout.groupby(mutation_key)['t_alt_count_fragment'].aggregate(lambda x :(x>=alt_thres).sum())

    # Find the number of sample with the Total Depth is >0
    # 't_vaf_fragment' column is NA for samples where mutation had no coverage, so count() will exclude it
    summary_table[fillout_type + 'n_fillout_sample'] = df_fillout.groupby(mutation_key)['t_vaf_fragment'].count()
    return summary_table
 

def extract_tn_genotypes(df_tumor, df_normal, df_ds_tumor, t_samplename, n_samplename):
    df_tn_genotype = df_tumor[df_tumor['Tumor_Sample_Barcode']==t_samplename][['t_alt_count_fragment', 't_ref_count_fragment','t_vaf_fragment']]

    if df_tn_genotype.shape[0] == 0:
        raise Exception('Tumor Sample ID {} not found in maf file'.format(t_samplename))

    df_ds_genotype = df_ds_tumor[df_ds_tumor['Tumor_Sample_Barcode']==t_samplename+'-SIMPLEX-DUPLEX'][['t_alt_count_fragment', 't_ref_count_fragment','t_vaf_fragment']]
    df_ds_genotype.rename(columns = {'t_alt_count_fragment':'SD_t_alt_count_fragment', 't_ref_count_fragment':'SD_t_ref_count_fragment','t_vaf_fragment':'SD_t_vaf_fragment'}, inplace=True)
    df_tn_genotype = df_tn_genotype.merge(df_ds_genotype, left_index=True, right_index=True)
    if n_samplename != '':
        df_n_genotype = df_normal[df_normal['Tumor_Sample_Barcode']==n_samplename][['t_alt_count_fragment', 't_ref_count_fragment','t_vaf_fragment']]
        df_n_genotype.rename(columns = {'t_alt_count_fragment':'n_alt_count_fragment', 't_ref_count_fragment':'n_ref_count_fragment','t_vaf_fragment':'n_vaf_fragment'}, inplace=True)
        df_n_genotype.insert(0, 'Matched_Norm_Sample_Barcode', n_samplename)        
        df_tn_genotype = df_tn_genotype.merge(df_n_genotype, left_index=True, right_index=True)
    return df_tn_genotype


def make_pre_filtered_maf(args):
    
    df_annotation = convert_annomaf_to_df(args)
    df_full_fillout = convert_fillout_to_df(args)
    df_tumor, df_normal, df_ds_tumor, df_curated, df_ds_curated=extract_fillout_type(df_full_fillout)
    
    df_tumor_summary = create_fillout_summary (df_tumor, args.tumor_detect_alt_thres)
    #tag tumor sample names with Duplex    
    for f in list(df_tumor_summary):
        if f not in ['POOL_median_VAF','POOL_n_fillout_sample_alt_detect',  'POOL_n_fillout_sample']:
            df_tumor_summary.rename(columns={f:f+'-DUPLEX'}, inplace=True)
    
    if df_normal.empty:
        df_normal_summary=pd.DataFrame(index=df_tumor_summary.index.copy())
        df_normal_summary['NORMAL_median_VAF']="no_normals_in_pool"
        df_normal_summary['NORMAL_n_fillout_sample_alt_detect']="no_normals_in_pool"
        df_normal_summary['NORMAL_n_fillout_sample']="no_normals_in_pool"
    else:
        df_normal_summary = create_fillout_summary (df_normal, args.tumor_detect_alt_thres)
        #tag normal as NORMAL        
        for f in list(df_normal_summary):
            if f not in ['NORMAL_median_VAF','NORMAL_n_fillout_sample_alt_detect',  'NORMAL_n_fillout_sample']:
                df_normal_summary.rename(columns={f:f+'-NORMAL'}, inplace=True)

    df_curated_summary = create_fillout_summary (df_curated, args.curated_detect_alt_thres)
    df_ds_tumor_summary = create_fillout_summary (df_ds_tumor, args.DS_tumor_detect_alt_thres)
    df_ds_curated_summary = create_fillout_summary (df_ds_curated, args.DS_curated_detect_alt_thres)
    
    df_tn_geno = extract_tn_genotypes(df_tumor, df_normal, df_ds_tumor, args.tumor_samplename, args.normal_samplename)
    df_pre_filter = df_annotation.merge(df_tn_geno, left_index=True, right_index=True).merge(df_tumor_summary, left_index=True, right_index=True).merge(df_ds_tumor_summary, left_index=True, right_index=True).merge(df_normal_summary, left_index=True, right_index=True).merge(df_curated_summary, left_index=True, right_index=True).merge(df_ds_curated_summary, left_index=True, right_index=True)
 
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
    
    #Occurrence in curated  n_fillout_sample_detect_min)
    parser.add_argument("--min_n_curated_samples_alt_detected", default=2, type=int, help="The Minimum number of curated samples variant is detected to be flagged")
    
    #Occurence in curated  n_fillout_sample_detect_min)
    parser.add_argument("--tn_ratio_thres", default=5, type=int, help="Tumor-Normal variant fraction ratio threshold")
    
    #Optional Blacklist
    parser.add_argument("--blacklist_file", default='', type=str, help="Filepath for Blacklist text file")

    args = parser.parse_args()
    return args


def apply_filter_maf (df_pre_filter, blacklist, args):
###=======FILTERS=======###
    def tag_germline(mut, status, args):
        #if there is a matched normal and it has sufficient coverage
        if 'n_vaf_fragment' in mut.index.tolist() and mut['n_ref_count_fragment'] + mut['n_alt_count_fragment'] > args.normal_TD_min:
            if mut['n_vaf_fragment'] > args.normal_vaf_germline_thres:
                status = status + 'Germline;'
        elif 'common_variant' in mut['FILTER'] and mut['t_ref_count_fragment'] + mut['t_alt_count_fragment'] > args.tumor_TD_min and mut['t_vaf_fragment'] > args.tumor_vaf_germline_thres:
            status = status + 'LikelyGermline;'
        return status
       
    def tag_below_alt_threshold(mut, status, args):
        if mut['t_alt_count_fragment'] < args.tier_one_alt_min or (mut['hotspot_whitelist'] == False and mut['t_alt_count_fragment'] < args.tier_two_alt_min):
            if mut['caller_t_alt_count']>= args.tier_two_alt_min or (mut['hotspot_whitelist'] == True and mut['caller_t_alt_count'] >= args.tier_one_alt_min):
                status = status+'BelowAltThreshold;LostbyGenotyper;'
            else:
                status = status+'BelowAltThreshold;'
        return status
        # TODO: ASK MIKE: add truncated mutations to below threshold 'Nonsense_Mutation', 'Splice_Site', 'Frame_Shift_Ins', 'Frame_Shift_Del'
        
    def occurrence_in_curated (mut, status, args):
        if mut['CURATED-DUPLEX_n_fillout_sample_alt_detect'] > args.min_n_curated_samples_alt_detected:
            status = status + 'InCurated;'
        return status
    
    def occurrence_in_normal (mut, status, args):
        #if normal and tumor coverage is greater than the minimal
        if mut['t_ref_count_fragment'] + mut['t_alt_count_fragment'] > args.tumor_TD_min:
            if mut['CURATED-DUPLEX_median_VAF'] != 0:
                if mut['t_vaf_fragment'] / mut['CURATED-DUPLEX_median_VAF'] < args.tn_ratio_thres:
                    status = status + 'TNRatio-curatedmedian;'
            
            if 'n_vaf_fragment' in mut.index.tolist():
                if mut['n_ref_count_fragment'] + mut['n_alt_count_fragment'] > args.normal_TD_min and mut['n_vaf_fragment'] != 0:
                    if mut['t_vaf_fragment'] / mut['n_vaf_fragment'] < args.tn_ratio_thres:
                        status = status + 'TNRatio-matchnorm;'
        return status
    
    def in_blacklist (mut, status, blacklist):
        #if mutation is listed in blacklist
        if str(mut['Chromosome'])+"_"+ str(mut['Start_Position'])+"_"+str(mut['End_Position'])+"_"+str(mut['Reference_Allele'])+"_"+str(mut['Tumor_Seq_Allele2']) in blacklist:
            status = status + 'InBlacklist;'
        return status

###=======Cleanup=======###
    def cleanup_post_filter(df_post_filter):
        #Change duplex columns to have D_ 
        df_post_filter.rename(columns ={'t_alt_count_fragment':'D_t_alt_count_fragment', 't_ref_count_fragment':'D_t_ref_count_fragment', 't_vaf_fragment':'D_t_vaf_fragment'}, inplace=True)        
        #Move Status column next to Hotspots
        col=list(df_post_filter)
        col.insert(col.index('D_t_alt_count_fragment'), col.pop(col.index('Status')))
        df_post_filter = df_post_filter[col]
        #Add Match Normal columns even when sample is unmatched
        if 'Matched_Norm_Sample_Barcode' not in col:
            df_post_filter.insert(col.index('SD_t_vaf_fragment')+1,'Matched_Norm_Sample_Barcode',"Unmatched")
            df_post_filter.insert(col.index('SD_t_vaf_fragment')+2,'n_alt_count_fragment',"NA")
            df_post_filter.insert(col.index('SD_t_vaf_fragment')+3,'n_ref_count_fragment',"NA")
            df_post_filter.insert(col.index('SD_t_vaf_fragment')+4,'n_vaf_fragment',"NA")
        #Always add a column with Matched_Norm_Bamfile 
        #TODO: ADD filename here
        col=list(df_post_filter)
        df_post_filter.insert(col.index('Matched_Norm_Sample_Barcode')+1,'Matched_Norm_Bamfile',"NA")
        return df_post_filter
    
###=======RUN=======###
    df_post_filter = df_pre_filter.copy()

    df_post_filter['Status'] = ''
    for i, mut in df_post_filter.iterrows():
        status = ''
        status = tag_germline(mut, status, args)
        status = tag_below_alt_threshold(mut, status, args)
        status = occurrence_in_curated(mut, status, args)
        status = occurrence_in_normal(mut, status, args)
        status = in_blacklist (mut, status, blacklist)
        df_post_filter.loc[i, 'Status'] = status
    
    df_post_filter=cleanup_post_filter(df_post_filter)

    return df_post_filter


def make_condensed_post_filter (df_post_filter):
    def grep(yourlist, yourstring):
         item= [item for item in yourlist if re.search(yourstring, item)]
         return item
    #Make Total depth Columns
    df_selected=df_post_filter.loc[df_post_filter['Status']=='']
    df_selected['SD_t_depth_count_fragment']=df_selected['SD_t_alt_count_fragment']+df_selected['SD_t_ref_count_fragment']

    if len(df_selected) and df_selected.n_alt_count_fragment[0] == 'NA':
        # Unmatched mode, no normal, can't calculate n_depth
        df_selected['n_depth_count_fragment'] = 'NA'
    else:
        df_selected['n_depth_count_fragment']=df_selected['n_alt_count_fragment']+df_selected['n_ref_count_fragment']

    #Find list columns to keep in order
    keep=['Tumor_Sample_Barcode','caller_Norm_Sample_Barcode','Matched_Norm_Sample_Barcode', 'Chromosome','Start_Position', 'Reference_Allele',	'Tumor_Seq_Allele2', 'Variant_Classification','Hugo_Symbol','HGVSp_Short','HGVSc','all_effects','dbSNP_RS','hotspot_whitelist','ExAC_AF','CallMethod', 'SD_t_depth_count_fragment',	'SD_t_alt_count_fragment',	'SD_t_ref_count_fragment',	'SD_t_vaf_fragment','n_depth_count_fragment',	'n_alt_count_fragment',	'n_ref_count_fragment',	'n_vaf_fragment']
    col=list(df_post_filter)

    # We want columns related to simplex-duplex values
    sd_keep=grep(col,'(-SIMPLEX-DUPLEX)')

    # We don't want columns related to curated values
    toremove = grep(sd_keep, '(CURATED)')
    for t in toremove:
        sd_keep.remove(t)

    keep.extend(sd_keep)

    # We want columns related to normal values
    keep.extend(grep(col,'(-NORMAL)'))

    df_condensed=df_selected[keep]
    return df_condensed
    

def main():
    args = parse_arguments()
    blacklist=extract_blacklist(args)
    df_pre_filter = make_pre_filtered_maf(args)
    df_post_filter = apply_filter_maf(df_pre_filter, blacklist, args)
    df_condensed = make_condensed_post_filter (df_post_filter)

    full_outfile_name = os.path.basename(args.fillout_maf).replace('.maf', '_filtered.maf')
    condensed_outfile_name = os.path.basename(args.fillout_maf).replace('.maf', '_filtered_condensed.maf')
    df_post_filter.to_csv(full_outfile_name, header=True, index=None, sep='\t')
    df_condensed.to_csv(condensed_outfile_name, header=True, index=None, sep='\t')

if __name__ == '__main__':
    main()
