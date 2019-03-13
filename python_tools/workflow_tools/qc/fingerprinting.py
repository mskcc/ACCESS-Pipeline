#!python


"""
Created on Thu May  3 11:36:00 2018
@author: hasanm
Fingerprinting script following edits. with major Contamination in order,
the filename in the pileup file as the first column, and Fixed the waltz directory can now be anything
Cleaned code with exception handling and  arg parse
Adapted newFP4.py to Luna
"""

from __future__ import division
import csv
import logging
import itertools
import numpy as np
import argparse
import pandas as pd
from PyPDF2 import PdfFileMerger

from ...constants import *
from ...util import extract_sample_name, read_df, get_position_by_substring

import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns



###################
# Helper Functions
###################

def read_csv(filename):
    # Todo: use Pandas instead
    data = []
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            data.append(row)
    return data


def write_csv(filename, data):
    with open(filename, 'a') as f:
        writer = csv.writer(f, delimiter='\t')
        for row in data:
            writer.writerow(row)


def merge_pdf_in_folder(out_dir, filename):
    merger = PdfFileMerger()

    pdfs = [x for x in os.listdir(out_dir) if '.pdf' in x]
    pdfs.sort()
    if len(pdfs) > 1:
        for pdf in pdfs:
            merger.append(open(out_dir + pdf, 'rb'))

        with open(out_dir + 'FPFigures.pdf', 'wb') as fout:
            merger.write(fout)
    else:
        raise IOError('Error: ' + filename + ' not created, input folder does not have PDFs to merge')


def make_output_dir(output_dir, dir_name):
    if os.path.exists(output_dir):
        if os.path.exists(output_dir + '/' + dir_name):
            raise IOError(
                'Error ' + dir_name + ' already exist in the OutputDir, either remove or rename Older directory')
        else:
            os.mkdir(output_dir + '/' + dir_name)
            return output_dir + '/' + dir_name + '/'
    else:
        raise IOError('Error: Output directory does not exist')


###################
# Extract RawData Functions
###################
def extract_pileup_files(input_dir):
    listofpileups = []
    if os.path.isdir(input_dir):
        for pileupfile in os.listdir(input_dir):
            if pileupfile.endswith("pileup.txt"):
                listofpileups.append(input_dir + '/' + pileupfile)
        return listofpileups
    else:
        raise IOError('Error: Input Directory with pileups does not exist')


def create_fp_indices(config_file):
    # Import config file.
    try:
        config = read_csv(config_file)
    except IOError:
        raise IOError('Error: FP configure file does not exist')
    # Check if there is a header and remove the header
    if config[0][0].lower() != 'Chrom'.lower():
        raise IOError('Error: FP configure has improper header')
    else:
        # Remove header and make index
        config.pop(0)
        fp_indices = dict()
        alleleInd = {'A': 4, 'C': 5, 'G': 6, 'T': 7}
        # Convert to Dict
        for f in config:
            if len(f) == 4:
                fp_indices[f[0] + ':' + f[1]] = [alleleInd[f[2]], alleleInd[f[3]], f[0] + ':' + f[1]]
            elif len(f) == 5:
                fp_indices[f[0] + ':' + f[1]] = [alleleInd[f[2]], alleleInd[f[3]], f[4]]
        n = len(fp_indices.keys())
        return fp_indices, n


def extract_list_of_tumor_samples(titlefile):
    title = read_csv(titlefile)
    listofsamples = [t[2] for i, t in enumerate(title) if t[5] == "Tumor"]
    return listofsamples


def concatenate_a_and_b_pileups(waltz_dir_a, waltz_dir_b, output_dir, dir_name, listofsamples=[]):
    merged_dir = make_output_dir(output_dir, dir_name)
    listofpileups = [p for p in os.listdir(waltz_dir_a) if p.endswith("-pileup.txt")]
    # Added: If you want to concatenate only some of the samples (i.e. Only Tumor Samples)
    if listofsamples:
        newlistofpileups = []
        for s in listofsamples:
            for p in listofpileups:
                if p.startswith(s):
                    newlistofpileups.append(p)
        listofpileups = newlistofpileups

    for p in listofpileups:
        if p in os.listdir(waltz_dir_b):
            a = read_csv(waltz_dir_a + '/' + p)
            b = read_csv(waltz_dir_b + '/' + p)
            a.extend(b)
            # this is not a uniq list. extractRawFP makes sure FP pileups are unique.
            write_csv(merged_dir + '/' + p, a)
        else:
            raise IOError(p + " not in WaltzDirB so pileup not concatenated and sample not fingerprinted")
    return merged_dir


###################
# Run Analysis
###################

def extract_raw_fp(pileupfile, fp_indices):
    pileup = read_csv(pileupfile)
    fpRaw = []
    for p in pileup:
        if p[0] + ':' + p[1] in fp_indices.keys() and p[0] + ':' + p[1] not in [f[0] + ':' + f[1] for f in fpRaw]:
            fpRaw.append(p[0:8])
    name = os.path.basename(pileupfile)
    fpRaw.insert(0, [name])
    return fpRaw


def find_fp_maf(listofpileups, fp_indices, fp_output_dir):
    all_fp = []
    all_geno = []
    alleles = ['A', 'C', 'G', 'T']
    thres = 0.1

    for pileupfile in listofpileups:
        fp_raw = extract_raw_fp(pileupfile, fp_indices)
        # writeCVS (fpOutputdir+'FP_counts.txt', fpRaw)
        name = fp_raw.pop(0)

        if all_fp == []:
            header = [fp_indices[eachfp[0] + ':' + eachfp[1]][2] for eachfp in fp_raw]
            header.insert(0, SAMPLE_ID_COLUMN)
            all_fp.append(header)
            all_geno.append(header)

        FPmAF = [min(counts) / sum(counts) if sum(counts) != 0 else 999 for counts in
                 [[int(eachfp[index]) for index in fp_indices[eachfp[0] + ':' + eachfp[1]][0:2]] for eachfp in fp_raw]]
        FPGeno = [alleles[np.argmax([int(F) for F in f[4::]])] if FPmAF[i] <= thres else "Het" for i, f in
                  enumerate(fp_raw)]

        FPmAF.insert(0, name[0])
        FPGeno.insert(0, name[0])
        all_fp.append(FPmAF)
        all_geno.append(FPGeno)

        for p in fp_raw:
            p.insert(0, name[0])

        write_csv(fp_output_dir + 'FP_counts.txt', fp_raw)

    write_csv(fp_output_dir + 'FP_mAF.txt', all_fp)
    write_csv(fp_output_dir + 'FP_Geno.txt', all_geno)
    return all_fp, all_geno


def contamination_rate(all_fp):
    contamination = []
    all_fp = all_fp[1::]
    for sample in all_fp:
        homozygous = [x for x in sample[1::] if x <= .1]
        if len(homozygous) != 0:
            contamination.append([sample[0], np.mean(homozygous)])
        else:
            contamination.append([sample[0], 'NaN'])
    return contamination


def create_expected_file(titlefile, fpOutputdir):
    title = read_csv(titlefile)
    samples = [t[2:5] for t in title]
    samples.pop(0)

    patient = {}

    for s in samples:
        if s[2] in patient.keys():
            patient[s[2]].append(s[0])
        else:
            patient[s[2]] = [s[0]]

    expected = []

    # Include each sample ID mapped to itself
    for sample in [t[0] for t in samples]:
        expected.append([sample, sample])

    for key, samples_per_patient in patient.items():
        if len(samples_per_patient) == 2:
            expected.append(samples_per_patient)
        elif len(samples_per_patient) > 2:
            for i, s1 in enumerate(samples_per_patient):
                for s2 in samples_per_patient[i + 1::]:
                    expected.append([s1, s2])
    if expected:
        write_csv(fpOutputdir + '/ExpectedMatches.txt', expected)
    return expected


def compare_genotype(all_geno, n, fp_output_dir, titlefile):
    expected = create_expected_file(titlefile, fp_output_dir)
    titlefile = read_df(titlefile, header='infer')

    if all_geno[0][0] == SAMPLE_ID_COLUMN:
        all_geno = all_geno[1::]

    all_geno = [a for a in all_geno if 'CELLFREEPOOLEDNORMAL' not in a[0]]
    geno_compare = []
    for i, Ref in enumerate(all_geno):
        for Query in all_geno:
            hm_Ref=0
            hm_match = 0
            hm_mismatch = 0
            ht_match = 0
            ht_mismatch = 0
            total_match = 0
            for j, element in enumerate(Ref):
                if element != 'Het':
                    hm_Ref= hm_Ref + 1
                if element == Query[j]:
                    total_match = total_match + 1
                    if element == 'Het':
                        ht_match = ht_match + 1
                    else:
                        hm_match = hm_match + 1
                elif element == 'Het' or Query[j] == 'Het':
                    ht_mismatch = ht_mismatch + 1
                elif j != 0:
                    hm_mismatch = hm_mismatch + 1

            sample_Ref = extract_sample_name(Ref[0], titlefile[SAMPLE_ID_COLUMN])
            sample_Query = extract_sample_name(Query[0], titlefile[SAMPLE_ID_COLUMN])
            
            ##To test            
            #sample_Ref = Ref[0].split("_IGO")[0]
            #sample_Query = Query[0].split("_IGO")[0]
            
            #Discordance rate between samples = Homozygous Mismatch/All Homozygous SNPs in Reference sample
            #Check that there are more the 10 Homozygous sites, if not, there is probably a lack of coverage or a lot of contamination
            if hm_Ref<10:
                discordance=np.nan
            else:
                discordance=hm_mismatch/(hm_Ref + EPSILON)
            
            geno_compare.append([sample_Ref, sample_Query, total_match, hm_match, hm_mismatch, ht_match, ht_mismatch, hm_Ref, discordance])

    sort_index = np.argsort([x[2] for x in geno_compare])
    geno_compare = [geno_compare[i] for i in sort_index]

    # Samples are considered matching if the discordance rate is less than 0.05
    mlist = [i for i, x in enumerate([g[8] for g in geno_compare]) if x < .05]

    if mlist != []:
        m = min(mlist)
    else:
        m = len(geno_compare)

    expectedInd = []
    for y in expected:
        for i, x in enumerate(geno_compare):
            if [x[0], x[1]] == y or [x[1], x[0]] == y:
                expectedInd.append(i)

    for i, x in enumerate(geno_compare):
        if i < m:
            if i in expectedInd:
                x.append('Unexpected Mismatch')
            else:
                x.append('Expected Mismatch')
        else:
            if i in expectedInd:
                x.append('Expected Match')
            else:
                x.append('Unexpected Match')

    geno_compare.insert(0, ["ReferenceSample", "QuerySample", "TotalMatch", "HomozygousMatch", "HomozygousMismatch",
                            "HeterozygousMatch", "HeterozygousMismatch", "HomozygousInRef","DiscordanceRate", "Status"])

    write_csv(fp_output_dir + 'Geno_compare.txt', geno_compare)

    return geno_compare


###################
##Plot Functions
###################

def plot_minor_contamination(all_fp, fp_output_dir, titlefile):
    plt.clf()
    contamination = contamination_rate(all_fp)
    contamination = [x for x in contamination if x[1] != 'NaN']
    titlefile = read_df(titlefile, header='infer')
    samplename = [extract_sample_name(c[0], titlefile[SAMPLE_ID_COLUMN]) for c in contamination]
    y_pos = np.arange(len(samplename))
    meanContam = [c[1] for c in contamination]
    minor_contamination = [[samplename[i], meanContam[i]] for i in range(0, len(samplename))]
    minor_contamination = sorted(minor_contamination)
    write_csv(fp_output_dir + 'minorContamination.txt', minor_contamination)

    plt.figure(figsize=(10, 5))
    plt.axhline(y=0.005, xmin=0, xmax=1, c='r', ls='--')
    plt.axhline(y=0.001, xmin=0, xmax=1, c='y', ls='--')

    plt.bar(y_pos, [m[1] for m in minor_contamination], align='edge', color='black')
    plt.xticks(y_pos, [m[0] for m in minor_contamination], rotation=90, ha='left')
    plt.ylabel('Avg. Minor Allele Frequency at Homozygous Position')
    plt.xlabel('Sample Name')
    plt.title('Minor Contamination Check (from all unique reads)')
    plt.xlim([0, y_pos.size])
    plt.savefig(fp_output_dir + '/MinorContaminationRate.pdf', bbox_inches='tight')


def plot_major_contamination(all_geno, fp_output_dir, titlefile):
    plt.clf()
    if all_geno[0][0] == SAMPLE_ID_COLUMN:
        all_geno = all_geno[1::]
    titlefile = read_df(titlefile, header='infer')
    samples = [extract_sample_name(g[0], titlefile[SAMPLE_ID_COLUMN]) for g in all_geno]
    x_pos = np.arange(len(all_geno))
    p_het = [sum([1 for a in g if a == 'Het']) / (len(g) - 1) for g in all_geno]

    major_contamination = [[samples[i], p_het[i]] for i in range(0, len(samples))]
    major_contamination = sorted(major_contamination)
    write_csv(fp_output_dir + 'majorContamination.txt', major_contamination)

    plt.axhline(y=0.6, xmin=0, xmax=1, c='r', ls='--')
    plt.bar(x_pos, [m[1] for m in major_contamination], align='edge', color='black')
    plt.xticks(x_pos, [m[0] for m in major_contamination], rotation=90, ha='left')
    plt.ylabel('Fraction of Heterozygous Position')
    plt.xlabel('Sample Name')
    plt.title('Major Contamination Check')
    plt.xlim([0, x_pos.size])
    plt.savefig(fp_output_dir + 'MajorContaminationRate.pdf', bbox_inches='tight')


def plot_duplex_minor_contamination(waltz_dir_a_duplex, waltz_dir_b_duplex, titlefile, output_dir, fp_indices, fp_output_dir):
    listofsamples = extract_list_of_tumor_samples(titlefile)
    if listofsamples:
        duplex_merged_dir = concatenate_a_and_b_pileups(waltz_dir_a_duplex, waltz_dir_b_duplex, output_dir, 'DuplexMergedPileup',
                                                    listofsamples)
        fp_duplex_output_dir = make_output_dir(fp_output_dir, 'FPDuplexResults')
        listofduplexpileups = extract_pileup_files(duplex_merged_dir)
        all_fp, all_geno = find_fp_maf(listofduplexpileups, fp_indices, fp_duplex_output_dir)

        # Plot the Contamination
        plt.clf()
        contamination = contamination_rate(all_fp)
        contamination = [x for x in contamination if x[1] != 'NaN']

        samplename = [c[0] for c in contamination]
        title_file = read_df(titlefile, header='infer')
        samplename = [extract_sample_name(s, title_file[SAMPLE_ID_COLUMN]) for s in samplename]

        y_pos = np.arange(len(samplename))
        mean_contam = [c[1] for c in contamination]
        minor_contamination = [[samplename[i], mean_contam[i]] for i in range(0, len(samplename))]
        minor_contamination = sorted(minor_contamination)
        write_csv(fp_output_dir + 'minorDuplexContamination.txt', minor_contamination)

        plt.figure(figsize=(10, 5))
        plt.axhline(y=0.005, xmin=0, xmax=1, c='r', ls='--')
        plt.axhline(y=0.001, xmin=0, xmax=1, c='y', ls='--')

        plt.bar(y_pos, [m[1] for m in minor_contamination], align='edge', color='black')
        plt.xticks(y_pos, [m[0] for m in minor_contamination], rotation=90, ha='left')
        plt.ylabel('Avg. Minor Allele Frequency at Homozygous Position')
        plt.xlabel('Sample Name')
        plt.title('Minor Contamination Check (Duplex)')
        plt.xlim([0, y_pos.size])
        plt.savefig(fp_output_dir + '/MinorDuplexContaminationRate.pdf', bbox_inches='tight')
    else:
        logging.warn("Duplex Minor Contamination plot: No Samples marked as Tumor in Titlefile")


def plot_genotyping_matrix(geno_compare, fp_output_dir, title_file):
    plt.clf()
    if geno_compare[0][0] == "ReferenceSample":
        geno_compare = geno_compare[1::]

    hm_compare = [[g[0],g[1],g[8]] for g in geno_compare]

    if len(hm_compare) == 0:
        # Only had one sample, and thus no comparisons to make
        titlefile = pd.read_csv(title_file, sep='\t')
        sample = titlefile[SAMPLE_ID_COLUMN].values[0]
        hm_compare = [[sample, sample, 0]]

    matrix ={}

    for element in hm_compare:
        if element[0] not in matrix.keys():
            matrix[element[0]] = {element[1]: element[2]}
        matrix[element[0]].update({element[1]: element[2]})

    plt.subplots(figsize=(8, 7))
    plt.title('Sample Mix-Ups')
    print(matrix)
    ax = sns.heatmap(pd.DataFrame.from_dict(matrix).astype(float), robust=True, annot=True, fmt='.2f', cmap="Blues_r", vmax=.15,
                     cbar_kws={'label': 'Fraction Mismatch'},
                     annot_kws={'size': 5})

    plt.savefig(fp_output_dir + 'GenoMatrix.pdf', bbox_inches='tight')

    Match_status = [[x[0], x[1], x[9]] for x in geno_compare if
                    x[9] == 'Unexpected Mismatch' or x[9] == 'Unexpected Match']

    # Deduplicate forward and reverse matches
    Match_status = [sorted(match) for match in Match_status]
    Match_status = list(match for match, _ in itertools.groupby(Match_status))

    df = pd.DataFrame(Match_status, columns=["Sample1", "Sample2", "Status"])
    Match_status.insert(0, ["Sample1", "Sample2", "Status"])

    write_csv(fp_output_dir + 'Match_status.txt', Match_status)

    plt.clf()
    fig, ax1 = plt.subplots()

    ax1.axis('off')
    ax1.axis('tight')
    if len(df.values):
        ax1.table(cellText=df.values, colLabels=df.columns, loc='center')
    else:
        empty_values = [['No mismatches present', 'No mismatches present', 'No mismatches present']]
        ax1.table(cellText=empty_values, colLabels=df.columns, loc='center')
    fig.tight_layout()

    plt.savefig(fp_output_dir + 'Geno_Match_status.pdf', bbox_inches='tight')


def find_sex_from_pileup(waltz_dir, output_dir):
    """
    Not Currently Used: Checks the pileups if there are more that 200 positions in the Y chromosome,
    with at least 1 read, the sample is classified as male.

    :param waltz_dir:
    :param output_dir:
    :return:
    """
    sex = []
    for file in os.listdir(waltz_dir):
        if file[-10::] == 'pileup.txt':
            data = []
            with open(waltz_dir + '/' + file, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                for row in reader:
                    if row[0] == 'Y':
                        if int(row[3]) > 0:
                            data.append(row[3])
            if len(data) > 200:
                sex.append([file[0:file.find('_bc')], "Male"])
            else:
                sex.append([file[0:file.find('_bc')], "Female"])
    write_csv(output_dir + '/Sample_sex_from_pileup.txt', sex)
    return sex


def find_sex_from_interval(waltz_dir):
    """
    Used: Checks the Interval files if the sum of the average coverage per interval (2 on Y) is greater that 50,
    the sample is classified as male.

    :param waltz_dir:
    :return:
    """
    sex = []
    for file in os.listdir(waltz_dir):
        if file[-13::] == 'intervals.txt':
            data = []
            with open(waltz_dir + '/' + file, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                for row in reader:
                    if row[3] == 'Tiling_SRY_Y:2655301' or row[3] == 'Tiling_USP9Y_Y:14891501':
                        data.append(int(row[5]))
            if sum(data) > 50:
                sex.append([file, "Male"])
            else:
                sex.append([file, "Female"])
    # writeCVS(OutputDir + '/Sample_sex_from_pileup.txt', sex)
    return sex


def standardize_gender(title_file):
    # Potential inputs
    female = ['female', 'f', 'Female', 'F']
    male = ['Male', 'M', 'male', 'm']

    title_info = read_csv(title_file)
    gender_from_title = [[t[2], t[11]] for t in title_info]
    gender = []
    for s in gender_from_title:
        if s[1] in female:
            gender.append([s[0], 'Female'])
        elif s[1] in male:
            gender.append([s[0], 'Male'])
    return gender


def check_sex(gender, sex, output_dir):
    list_of_samples = [s[0] for s in sex]
    mismatch_sex = []
    for g in gender:
        idx = get_position_by_substring(g[0], list_of_samples)
        if g[1] != sex[idx][1]:
            mismatch_sex.append([g[0], g[1], sex[idx][1]])

    df = pd.DataFrame(mismatch_sex, columns=[SAMPLE_ID_COLUMN, "Reported Sex", "Inferred Sex"])
    if not len(df):
        df.loc[0] = ['No mismatches present', 'No mismatches present', 'No mismatches present']

    write_csv(output_dir + '/MisMatchedGender.txt', mismatch_sex)
    plt.clf()
    fig, ax = plt.subplots()
    plt.title('Sex MisMatch')
    ax.axis('off')
    ax.axis('tight')
    ax.table(cellText=df.values, colLabels=df.columns, loc='center')
    fig.tight_layout()
    plt.savefig(output_dir + '/GenderMisMatch.pdf', bbox_inches='tight')


######################
# Convert Txt files
######################

def convert_fp_maf(input_dir):
    x = read_csv(input_dir + 'FP_mAF.txt')
    all_fp = []
    for sample in x[1::]:
        new = [float(i) for i in sample[1::]]
        new.insert(0, sample[0])
        all_fp.append(new)
    all_fp.insert(0, x[0])
    return all_fp


######################
# Main Function
######################

def run_fp_report(output_dir, waltz_dir_a, waltz_dir_b, waltz_dir_a_duplex, waltz_dir_b_duplex, config_file, titlefile):
    merged_dir = concatenate_a_and_b_pileups(waltz_dir_a, waltz_dir_b, output_dir, 'MergedPileup')
    listofpileups = extract_pileup_files(merged_dir)
    fp_indices, n = create_fp_indices(config_file)
    fp_output_dir = make_output_dir(output_dir, 'FPResults')
    all_fp, all_geno = find_fp_maf(listofpileups, fp_indices, fp_output_dir)

    # Contamination plots
    plot_minor_contamination(all_fp, fp_output_dir, titlefile)
    plot_major_contamination(all_geno, fp_output_dir, titlefile)

    # plotGenoCompare(geno_compare,n, fpOutputdir)
    geno_compare = compare_genotype(all_geno, n, fp_output_dir, titlefile)
    plot_genotyping_matrix(geno_compare, fp_output_dir, titlefile)

    # Duplex Plot
    plot_duplex_minor_contamination(waltz_dir_a_duplex, waltz_dir_b_duplex, titlefile, output_dir, fp_indices, fp_output_dir)
    merge_pdf_in_folder(fp_output_dir, 'FPFigures.pdf')

    # return listofpileups, fpIndices, n, All_FP, All_geno, Geno_Compare


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_dir", help="Directory to write the Output files to", required=True)
    parser.add_argument("-a", "--waltz_dir_A", help="Directory with waltz pileup files for target set A", required=True)
    parser.add_argument("-b", "--waltz_dir_B", help="Directory with waltz pileup files for target set B", required=True)
    parser.add_argument("-da", "--waltz_dir_A_duplex", help="Directory with waltz pileup files for Duplex target set A",
                        required=True)
    parser.add_argument("-db", "--waltz_dir_B_duplex", help="Directory with waltz pileup files for Duplex target set B",
                        required=True)
    parser.add_argument("-c", "--fp_config", help="File with information about the SNPs for analysis", required=True)
    parser.add_argument("-t", "--title_file", help="Title File for the run", required=False)
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

    # Fingerprinting
    run_fp_report(output_dir=args.output_dir, waltz_dir_a=args.waltz_dir_A, waltz_dir_b=args.waltz_dir_B,
                    waltz_dir_a_duplex=args.waltz_dir_A_duplex, waltz_dir_b_duplex=args.waltz_dir_B_duplex,
                    config_file=args.fp_config, titlefile=args.title_file)

    # Sex
    gender = standardize_gender(title_file=args.title_file)
    sex = find_sex_from_interval(waltz_dir=args.waltz_dir_B)
    check_sex(gender, sex, output_dir=args.output_dir)


if __name__ == '__main__':
    main()
