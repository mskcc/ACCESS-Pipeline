#!/usr/bin/env python

"""
ADMIE Analysis Utility

Used to run the full ADMIE pipeline

@author: Preethi Srinivasan, John Ziegler
Memorial Sloan Kettering Cancer Center
May 2019

"""
import argparse
import os
import numpy as np
import pandas as pd
import time
import math
from joblib import dump, load

# Relative imports for supporting scripts
from cwl_tools.msi.scripts.calculate_distances import create_output_file
from cwl_tools.msi.scripts.predict import predict

# Global variables
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))



def main():
    parser = argparse.ArgumentParser(description="ADMIE Analysis")
    
    parser.add_argument(
        "--allele-list",
        nargs='+', 
        help='Full paths to Allele Counts files output from MSIsensor'
    )


    parser.add_argument(
        "--allele-counts",
        default=ROOT_DIR + "/allele-counts/",
        help="Allele Counts output from MSIsensor"
    )

    parser.add_argument(
        "--model",
        default=ROOT_DIR + "/ACCESS_SVM.model",
        help="SVM model to classify cfDNA samples"
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
        default=True,
        help="Generate QC pdf reports for every sample included in input directory"
    )
    
    parser.add_argument(
        "--qc-directory",
        default="",
        help="Optional directory to indicate files to be used for average site coverage calculation"
    )

    parser.add_argument(
        "--result-file",
        default="msi_results.txt",
        help="output file to save results to"
    )

    args = parser.parse_args()
    analysis_dir = args.allele_counts
    model = args.model
    output_file = args.output_file
    save_format = args.save_format
    generate_qc = args.generate_qc
    qc_directory = args.qc_directory
    result_file = args.result_file
    allele_counts_files = args.allele_list # in case we want to pass files as a list instead of dir

    # Create the distance vectors and persist it to disk as a 
    # tsv file
    create_output_file(analysis_dir, output_file, save_format, generate_qc, allele_counts_files)
    
    # Run the prediction
    predict(output_file, model, qc_directory, result_file)

    # TODO Add QC check here
    


if __name__ == "__main__":
    main()
