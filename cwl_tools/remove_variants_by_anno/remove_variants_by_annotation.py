#!python

# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 14:26:35 2019

@author: hasanm
"""

import pandas as pd
import logging
import argparse
import time
import re
#import sys
        
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=logging.DEBUG)
logger = logging.getLogger('remove_variants_by_annotation_w_hotspots')        
        
#Can add here: Check Hotspot List

#Check RefSeq list
def check_interval(input_interval):
    try:
        df_intervals=pd.read_csv(input_interval,sep='\t', header=0)
        #Takes the first column and checks that there is any ensembl transcript ids or refseq ids with version
        import warnings
        warnings.filterwarnings("ignore", 'This pattern has match groups')
        if df_intervals.iloc[:,0].str.contains('^(NM_\d{1,}\.\d{1,})$|^(ENST\d{1,})$', case=True, regex=True).all():
            return df_intervals.iloc[:,0].unique().tolist()
        else:
            raise ValueError 
    except KeyError:
        #print('There is no RefSeq Column in the inputted interval file')
        logging.error('There is no RefSeq Column in the inputted interval file')
        raise
    except OSError:
        #print('Inputted interval file does not exist')
        logging.error('Inputted interval file does not exist')
        raise
    except ValueError:
        #print('Inputted interval file does not contain only RefSeq IDs or the version numbers for canonical transcripts is missing (decimal in RefSeqIDs)')
        logging.error('Inputted interval file does not contain only RefSeq or Ensembl transcript IDs or the version numbers for canonical transcripts is missing (decimal in RefSeqIDs)')
        raise

#TO DO: Can add Tag Hotspots here
#def tag_hotspots(df_maf,args):

    
#Filter my Annotation: Input: vep.maf, flag_create_dropped_variants_maf,
#optional Input: RefSeq file
#output: kept.maf, Dropped.maf, notingenomicrange.maf
def filter_by_annotation(args):
    df_input = pd.read_csv(args.input_maf,sep='\t', header=1)
    keep_exonic = ['Missense_Mutation', 'Nonsense_Mutation', 'Splice_Site', 'Frame_Shift_Ins', 'Frame_Shift_Del', 'In_Frame_Ins', 'In_Frame_Del', 'Translation_Start_Site', 'Nonstop_Mutation', 'Silent']

    Bool_exon = df_input['Variant_Classification'].isin(keep_exonic)   
    Bool_MET = (df_input['Variant_Classification']=='Intron') & (df_input['Hugo_Symbol']=='MET')
    Bool_TERT = (df_input['Variant_Classification']=="5'Flank") & (df_input['Hugo_Symbol']== 'TERT')
    #Removes based on Annotations
    df_kept = df_input[Bool_exon|Bool_MET|Bool_TERT]
    df_drop = df_input[~(Bool_exon|Bool_MET|Bool_TERT)]
    
    df_notinGenomicRange=pd.DataFrame()
    #Removes based on genomic Range
    if args.input_interval:
        intervals=check_interval(args.input_interval)
        Bool_inGenomicRange = df_kept['all_effects'].fillna('NA').apply(lambda x: any([y in intervals for y in re.split(',|;',x)]))
        df_notinGenomicRange = df_kept[~Bool_inGenomicRange]
        df_kept=df_kept[Bool_inGenomicRange]

    return df_drop, df_notinGenomicRange, df_kept


def parse_arguments():
    """
    Parse arguments for remove variants by annoation and hotspot tagging module

    :return:
    """
    parser = argparse.ArgumentParser(prog='Remove_by_Annotation_w_hotspots.py', description=' This tool helps to remove variant by annotation and genomic region, and tag hotspot events', usage='%(prog)s [options]')
    parser.add_argument('-i', '--input_maf', required=True, type=str, help='Input maf file which needs to be tagged')
    #parser.add_argument('-hotspots', '--input_hotspot', required=True, type=str, help='Input txt file which has hotspots')
    parser.add_argument('-interval', '--input_interval', required=False, default='', type=str, help='Optional: Input txt file which has RefSeq IDs for desired intervals')
    parser.add_argument('-kept','--kept_output_maf', required=True, type=str, help='Output maf of kept variants file name')
    parser.add_argument('-dropped','--dropped_output_maf', required=True, type=str, help='Output maf file name of dropped variants that are nonexonic')
    parser.add_argument('-dropped_NGR','--dropped_NGR_output_maf', required=True, type=str, help='Output maf file name of dropped variants not in Genomic Range')        
    args = parser.parse_args()
    return args

def main():
    args = parse_arguments()
    df_drop, df_notinGenomicRange, df_kept = filter_by_annotation(args)
    
    df_notinGenomicRange.to_csv(args.dropped_NGR_output_maf, sep='\t', index=False)
    df_drop.to_csv(args.dropped_output_maf, sep='\t', index=False)
    df_kept.to_csv(args.kept_output_maf, sep='\t', index=False)

if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()

    totaltime = end_time - start_time
    logging.info('remove_variants_by_annotation_w_hotspots: Elapsed time was %g seconds', totaltime)