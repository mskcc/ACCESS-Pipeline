"""
ADMIE Distance Calculation Utility

Used to generate a tsv file detailing the distance metrics for each 
loci in every sample found in the input directory.

Each line is tab-seperated outlining the normalized allele counts for both
the tumor and normal sample at the indicated location

@author: Preethi Srinivasan, John Ziegler
Memorial Sloan Kettering Cancer Center
May 2019

"""

import os
import numpy as np
import pandas as pd
import time
import math
from joblib import dump, load
import argparse
import matplotlib
import matplotlib.backends.backend_pdf
import matplotlib.pyplot as plt
import seaborn as sns

# Global variables
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def _normTotalCoverage(p):
    try:
        norm = [i/float(sum(p)) for i in p]
    except ZeroDivisionError:
        norm = [i for i in p]
    return norm

def _get_n_alleles(list_tumor, list_normal):
    #list_tumor = list_tumor[1:-1].split(",")
    #list_tumor = [float(i) for i in list_tumor]
    #list_normal = list_normal[1:-1].split(",")
    #list_normal = [float(i) for i in list_normal]
    list_tumor = [i for i in list_tumor if i >= 5]
    list_normal = [i for i in list_normal if i >= 5] 
    
    n_alleles = len(list_tumor) - len(list_normal)
    return n_alleles


def _processLine(count_line):
    sample_counts = count_line.split(":")[1].split(" ")[1:]
    sample_counts = [float(i) for i in sample_counts if i != '']
    
    return sample_counts, _normTotalCoverage(sample_counts)

def _processTumorNormalBlock(location, normal, tumor, allele_count_file):
    results = []
    location = location.strip().split(" ")
    chr_location = location[0]+":"+location[1]
    
    normal = normal.strip()                
    # Verify that this line is indeed the Normal
    if normal.startswith("N"):
        try:
            normal_counts, normalized_normal_counts = _processLine(normal)
            total_norm_normal_counts = np.sum(normalized_normal_counts)
        except ValueError:
            print("Parsing issue while processing Normal: " + chr_location + " in file: " + allele_count_file)
 
    tumor = tumor.strip()
    # Verify that this line is the Tumor
    if tumor.startswith("T"):
        try:
            tumor_counts, normalized_tumor_counts = _processLine(tumor)
            total_norm_tumor_counts = np.sum(normalized_tumor_counts)
        except ValueError:
            print("Parsing issue while processing Tumor: " + chr_location + " in file: " + allele_count_file)

    n_alleles_diff = _get_n_alleles(tumor_counts, normal_counts)

    if(len(normalized_normal_counts)>0 and len(normalized_tumor_counts)>0):

        # calculate the normalized difference in allele counts 
        # between the tumor and the normal
        distance = [(normalized_tumor_counts[i]-normalized_normal_counts[i]) 
                    for i in range(0, len(normalized_tumor_counts))]
        distance = np.sum(distance)

        # calculate absolute distance normalized difference in 
        # allele counts between the tumor and the normal
        distance_abs = [math.fabs(normalized_tumor_counts[i]-normalized_normal_counts[i]) 
                        for i in range(0, len(normalized_tumor_counts))]
        distance_abs = np.sum(distance_abs)

        # Use the absolute value to do chisq test, need to verify the normalized tumor count is over zero 
        chisq = [math.fabs(normalized_tumor_counts[i]-normalized_normal_counts[i])/normalized_tumor_counts[i] 
                    if normalized_tumor_counts[i]>0 else 0 for i in range(0, len(tumor_counts))]

        chisq = np.sum(chisq)


        return {
            "Sample":allele_count_file[:-4], 
            "Location":chr_location, 
            "Normal": normal_counts,
            "Tumor": tumor_counts,
            "Normalized_Normal":normalized_normal_counts,
            "Normalized_Tumor":normalized_tumor_counts,
            "distance": distance,
            "distance_abs": distance_abs,
            "chisq": chisq,
            "cumulative_norm_norm":total_norm_normal_counts,
            "cumulative_norm_tumor":total_norm_tumor_counts,
            "n_alleles_diff":n_alleles_diff,
        }

    return None
    


def _processFile(full_path, filename):
    results = []
    with open(full_path) as f:
        lines = f.readlines()
        # The lines are batched in sets of 3, the first line is the locus,
        # the second is the normal, and the third is the tumor
        if len(lines) < 3:
            return None

        for idx in range(0, len(lines), 3):
            try:
                block_res = _processTumorNormalBlock(lines[idx], lines[idx+1], lines[idx+2], filename)
                if block_res is not None:
                    results.append(block_res)
            
            except Exception as e:
                print("Error in file: " + filename)
                print(e)
                return None

    # TODO verify that the result has all 165 loci

    return results

def _generateQCFiles(results):
    sample_list = results['Sample'].unique().tolist()

    for sample in sample_list:
        df_important_regions = results[results['Sample']==sample][['Location',
                               'distance_abs']].sort_values('distance_abs',ascending = False)
        important_regions = df_important_regions['Location'].tolist()
    
        pdf = matplotlib.backends.backend_pdf.PdfPages(sample+"_MSI_QC.pdf")
        top_regions = important_regions[:10]

        for region in top_regions:
            df_plot = results[(results['Location']==region) &
                            (results['Sample'].str.startswith(sample))]
            tumor_coverage = df_plot[df_plot['Sample']==sample]['Tumor'].tolist()
            normal_coverage_std = df_plot[df_plot['Sample']==sample]['Normal'].tolist()


            tumor_coverage = tumor_coverage[0]
            #tumor_coverage = [float(i.strip()) for i in tumor_coverage]
            normal_coverage_std = normal_coverage_std[0]
            #normal_coverage_std = [float(i.strip()) for i in normal_coverage_std]
            #print(tumor_coverage)
            df_plot = pd.DataFrame(columns = [ 'Plasma', 'BC'])

            df_plot['Tumor'] = tumor_coverage
            df_plot['Normal'] = normal_coverage_std
            df_plot['location'] = df_plot.index + 1
            df_plot = df_plot[(df_plot['Tumor']>0) | df_plot['Normal']>0]
            if(df_plot.shape[0]>2):
                f, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(4, 4))
                f.subplots_adjust(left=0.2)
                sns.barplot(x = df_plot['location'], y = df_plot['Tumor'], color = 'black', ax = ax1,
                       label = 'Plasma').set_title(sample+" - "+region)
                ax1.set_ylabel("Coverage")
                ax1.set_xlabel("")

                sns.barplot(x = df_plot['location'], y = df_plot['Normal'], color = 'blue', ax = ax2,
                       label = 'BC')
                ax2.set_ylabel("Coverage")
                f.legend(loc='upper left', bbox_to_anchor=(0.86, 0.9), fancybox=False, shadow=False, frameon=False)

                ax2.xaxis.set_tick_params(labelsize=6)
                ax1.yaxis.set_tick_params(labelsize=8)
                ax2.yaxis.set_tick_params(labelsize=8)
                ax2.yaxis.set_label_coords(-0.15, 0.5)
                ax1.yaxis.set_label_coords(-0.15, 0.5)

                pdf.savefig( f, bbox_inches='tight' )
                plt.close(f)
        pdf.close()


def create_output_file(analysis_dir, output_filename, save_format, generate_qc_files):
    files_to_analyze = os.listdir(analysis_dir)
    files_to_analyze = [x for x in files_to_analyze if "_dis" in x]
    results =[]

    for allele_count_file in files_to_analyze:
        full_path = os.path.join(analysis_dir, allele_count_file)
        res = _processFile(full_path, allele_count_file)
        if res is not None: 
            results += res

    # TODO add logic to output different formats
    pd.DataFrame.from_records(results).to_csv(output_filename, sep = '\t', index = None)

    if generate_qc_files:
        _generateQCFiles(pd.DataFrame.from_records(results))

def main():
    parser = argparse.ArgumentParser(description="ADMIE Distance Calculation")
    parser.add_argument(
        "--allele-counts",
        default=ROOT_DIR + "/allele-counts/",
        help="Allele Counts output from MSIsensor"
    )

    parser.add_argument(
        "--output-file",
        default="distance_vectors.tsv",
        help="Name of the file that will be saved"
    )

    parser.add_argument(
        "--save-format",
        default="tsv",
        help="Format to save the output file"
    )

    parser.add_argument(
        "--generate-qc",
        action="store_true",
        default=False,
        help="Generate QC pdf reports for every sample included in input directory"
    )

    args = parser.parse_args()

    create_output_file(
        args.allele_counts,
        args.output_file,
        args.save_format,
        args.generate_qc,
    )


if __name__ == "__main__":
    main()




