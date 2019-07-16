"""
ADMIE Prediction Utility

Reads the tsv outputed by the distance calculation utility and predicts
the MSI phenotype from the distance vectors using our SVM model

@author: Preethi Srinivasan, John Ziegler
Memorial Sloan Kettering Cancer Center
May 2019

"""
import argparse
from sklearn import svm
import os
import numpy as np
import pandas as pd
import time
import math
from joblib import dump, load

# Global variables
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def _processQCCoverageFile(filepath):
    with open(filepath, "r") as f:
        lines = f.readlines()
        coverage_sum = 0
        site_count = 0
        for line in lines:
            if "msi" in line:
                line = line.split("\t")
                coverage_sum += float(line[-2])
                site_count+=1
    if site_count > 0:
        return coverage_sum/site_count
    return None

def _calculateCoverage(sample_list, qc_dir):
    qc_files = os.listdir(qc_dir)
    qc_files = [i for i in qc_files if i.endswith("intervals-without-duplicates.txt")]
    tumor_coverages = {}
    normal_coverages = {}
    for sample in sample_list:
        tumor_qc_file = [i for i in qc_files if sample in i]
        normal_qc_file = [i for i in qc_files if sample.replace("-T", "-N").replace("-L", "-N") in i]
        if len(tumor_qc_file) > 0:
            covg = _processQCCoverageFile(qc_dir + "/" + tumor_qc_file[0])
            tumor_coverages[sample] = covg
        if len(normal_qc_file) > 0:
            ncovg = _processQCCoverageFile(qc_dir + "/" + normal_qc_file[0])
            normal_coverages[sample] = ncovg
 
    return tumor_coverages, normal_coverages        


def predict(filename, model, qc_dir, result_file):
    #print("loading from filename: " + filename)
    # At this point we have all the sample information, distances, etc in the distance vectors file
    # so we will read it in and do our formal evaluation
    # Load our model from disk
    trained_svm = load(model)

    #full_path = os.path.join(ROOT_DIR, filename)
    cfDNA_data = pd.read_csv(filename, sep = '\t')
    
    #print("loaded_data")
    #print(cfDNA_data)
    # directionality is important, so this covers loci where the normal is more instable than the tumor
    cfDNA_data['distance_abs'] = np.where(cfDNA_data['chisq']==0, 0, cfDNA_data['distance_abs'])

    # calculate median alleles by sample
    median_alleles_by_sample = pd.DataFrame({
        'median_alleles': cfDNA_data.groupby(['Sample'])['n_alleles_diff'].median(),
    }).reset_index()

    median_alleles_by_sample['median_allele_direction'] = np.where(median_alleles_by_sample['median_alleles']>0, 1, 0)

    dict_number_of_alleles = dict(zip(
        median_alleles_by_sample['Sample'], 
        median_alleles_by_sample['median_allele_direction']))

    # create the vectors
    cfDNA_distances = cfDNA_data.pivot_table(index = 'Sample', columns = 'Location', values = 'distance_abs')
    cfDNA_distances = cfDNA_distances.reset_index()

    cfDNA_distances.columns = ["distance_"+i for i in cfDNA_distances.columns.tolist()]
    cfDNA_distances.columns = ["Sample"]+cfDNA_distances.columns.tolist()[1:]

    # add median allele count to vector as another feature
    cfDNA_distances['median_n_alleles'] = cfDNA_distances['Sample'].map(dict_number_of_alleles)

    # prep the table for prediction, no longer need column names
    cfDNA_distances.index = cfDNA_distances['Sample']
    cfDNA_distances = cfDNA_distances.drop('Sample', axis = 1)
    
    # run our actual prediction
    svm_predictions = trained_svm.predict(cfDNA_distances)
    svm_predictions_prob = trained_svm.decision_function(cfDNA_distances)

    cfDNA_distances['predicted_label'] = svm_predictions
    dict_predictions = dict(zip(cfDNA_distances.index, cfDNA_distances['predicted_label']))
    #print(svm_predictions)
    #print(svm_prediction_prob) 
    
    svm_predictions_prob = [i + 1.2 for i in svm_predictions_prob ]
    cfDNA_distances['predicted_label_proba'] = svm_predictions_prob
    dict_predictions_prob = dict(zip(cfDNA_distances.index, cfDNA_distances['predicted_label_proba']))

    # output results
    cfDNA_distances = cfDNA_distances.sort_values('predicted_label_proba')
    t_coverages = {}
    n_coverages = {}
    if qc_dir != "":
        t_coverages, n_coverages = _calculateCoverage(cfDNA_distances.index.tolist(),qc_dir)

    with open(result_file, "w") as f:
        f.write("Tumor_Sample_ID\tNormal_Sample_ID\tMSI_Status\tDistance_from_boundary\tMSI_Coverage_Tumor\tMSI_Coverage_Normal\n")
        for i in cfDNA_distances.index.tolist():
            classification = "NA"
            normal = i.replace("-T", "-N").replace("-L", "-N")
            if dict_predictions_prob[i] >= 0:
                classification = "MSI"

            tumor_coverage = "-"
            normal_coverage = "-"

            if i in t_coverages:
                tumor_coverage = str(t_coverages[i])

            if i in n_coverages:
                normal_coverage = str(n_coverages[i])
        
            #f.write(i+"\t"+normal+"\t"+classification+"\t"+str(dict_predictions_prob[i])+"\t"+tumor_coverage + "\t" + normal_coverage + "\n") 
            f.write(i.split(".")[0]+"\t"+normal.split(".")[0]+"\t"+classification+"\t"+str(dict_predictions_prob[i])+"\t"+tumor_coverage + "\t" + normal_coverage + "\n")


def main():
    parser = argparse.ArgumentParser(description="ADMIE Prediction Utility")

    parser.add_argument(
        "--output-file",
        default="distance_vectors.tsv",
        help="Name of the file containing distance vectors that will be read in"
    )

    parser.add_argument(
        "--model",
        default=ROOT_DIR + "/ACCESS_SVM.model",
        help="SVM model to classify cfDNA samples"
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
    predict(args.output_file, args.model, args.qc_directory, args.result_file)



if __name__ == "__main__":
    main()

