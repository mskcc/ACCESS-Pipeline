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
import os

from python_tools.constants import *
from python_tools.util import extract_sample_name, read_df, get_position_by_substring

import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns

PDF_FILENAMES = [
    'GenoMatrix.pdf',
    'Unexpected_Match.pdf',
    'Unexpected_Mismatch.pdf',
    'GenderMisMatch.pdf',
    'MinorContaminationRate.pdf',
    'MajorContaminationRate.pdf',
    'MinorDuplexContaminationRate.pdf',
]

FINAL_PDF_FILENAME = 'FPFigures.pdf'

###################
# Helper Functions
###################

def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


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
    pdfs = sorted(pdfs, key=lambda x: PDF_FILENAMES.index(x))

    if len(pdfs) > 1:
        for pdf in pdfs:
            merger.append(open(out_dir + pdf, 'rb'))

        with open(out_dir + FINAL_PDF_FILENAME, 'wb') as fout:
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
            header.insert(0, TITLE_FILE__SAMPLE_ID_COLUMN)
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
    
    if all_geno[0][0] == TITLE_FILE__SAMPLE_ID_COLUMN:
        all_geno = all_geno[1::]
    
    # TODO: come up with a better way to remove control samples
    # before fingerprinting analysis
    #all_geno = [a for a in all_geno if a[0] not in ALLOWED_CONTROLS]
    
    geno_compare = []
    for i, Ref in enumerate(all_geno):
        for Query in all_geno:
            hm_Ref = 0
            hm_match = 0
            hm_mismatch = 0
            ht_match = 0
            ht_mismatch = 0
            total_match = 0
            for j, element in enumerate(Ref):
                if element != 'Het':
                    hm_Ref = hm_Ref + 1
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

            sample_Ref = extract_sample_name(Ref[0], titlefile[TITLE_FILE__SAMPLE_ID_COLUMN])
            sample_Query = extract_sample_name(Query[0], titlefile[TITLE_FILE__SAMPLE_ID_COLUMN])
            
            ##To test            
            #sample_Ref = Ref[0].split("_IGO")[0]
            #sample_Query = Query[0].split("_IGO")[0]
            
            #Discordance rate between samples = Homozygous Mismatch/All Homozygous SNPs in Reference sample
            #Check that there are more the 10 Homozygous sites, if not, there is probably a lack of coverage or a lot of contamination
            if hm_Ref<10:
                discordance=np.nan
            else:
                discordance = hm_mismatch / (hm_Ref + EPSILON)

            geno_compare.append(
                [sample_Ref, sample_Query, total_match, hm_match, hm_mismatch, ht_match, ht_mismatch, hm_Ref,
                 discordance])

    sort_index = np.argsort([x[2] for x in geno_compare])
    geno_compare = [geno_compare[i] for i in sort_index]

    # Samples are considered matching if the discordance rate is less than 0.05
    mlist = [i for i, x in enumerate([g[8] for g in geno_compare]) if x < .05]

    df = pd.DataFrame(geno_compare, columns=['ReferenceSample',
                                             'QuerySample',
                                             'TotalMatch',
                                             'HomozygousMatch',
                                             'HomozygousMismatch',
                                             'HeterozygousMatch',
                                             'HeterozygousMismatch',
                                             'HomozygousInRef',
                                             'DiscordanceRate'])

    expected.extend([[i[1], i[0]] for i in expected])
    df_expected = pd.DataFrame(expected, columns=['ReferenceSample', 'QuerySample'])
    df_expected.drop_duplicates(inplace=True)
    df_expected['Expected'] = True
    df = df.merge(df_expected, on=['ReferenceSample', 'QuerySample'], how='outer')
    df['Expected'] = df['Expected'].fillna(value=False)

    matched = [geno_compare[i][0:2] for i in mlist]
    df_matched = pd.DataFrame(matched, columns=['ReferenceSample', 'QuerySample'])
    df_matched['Matched'] = True
    df = df.merge(df_matched, on=['ReferenceSample', 'QuerySample'], how='outer')
    df['Matched'] = df['Matched'].fillna(value=False)

    df.loc[df.Matched & df.Expected, 'Status'] = "Expected Match"
    df.loc[df.Matched & ~df.Expected, 'Status'] = "Unexpected Match"
    df.loc[~df.Matched & df.Expected, 'Status'] = "Unexpected Mismatch"
    df.loc[~df.Matched & ~df.Expected, 'Status'] = "Expected Mismatch"
    df.drop(['Matched', 'Expected'], axis=1, inplace=True)
    geno_compare = df.values.tolist()
    geno_compare.insert(0, ["ReferenceSample", "QuerySample", "TotalMatch", "HomozygousMatch", "HomozygousMismatch",
                            "HeterozygousMatch", "HeterozygousMismatch", "HomozygousInRef", "DiscordanceRate",
                            "Status"])

    write_csv(fp_output_dir + 'Geno_compare.txt', geno_compare)

    return geno_compare


###################
##Plot Functions
###################

def plot_major_contamination(all_geno, fp_output_dir, titlefile):
    plt.clf()
    if all_geno[0][0] == TITLE_FILE__SAMPLE_ID_COLUMN:
        all_geno = all_geno[1::]
    titlefile = read_df(titlefile, header='infer')
    samples = [extract_sample_name(g[0], titlefile[TITLE_FILE__SAMPLE_ID_COLUMN]) for g in all_geno]
    x_pos = np.arange(len(all_geno))
    p_het = [sum([1 for a in g if a == 'Het']) / (len(g) - 1) for g in all_geno]

    major_contamination = [[samples[i], p_het[i]] for i in range(0, len(samples))]
    major_contamination = sorted(major_contamination)
    write_csv(fp_output_dir + 'majorContamination.txt', major_contamination)

    plt.axhline(y=0.6, xmin=0, xmax=1, c='r', ls='--')
    plt.bar(x_pos, [m[1] for m in major_contamination], align='center', color='black')
    plt.xticks(x_pos, [m[0] for m in major_contamination], rotation=90, ha='center')
    plt.ylabel('Fraction of Heterozygous Position')
    plt.xlabel('Sample Name')
    plt.title('Major Contamination Check')
    plt.xlim([-1, x_pos.size])
    plt.savefig(fp_output_dir + 'MajorContaminationRate.pdf', bbox_inches='tight')


# TO DO MAKE title file columns into CONSTANTS to be imported
def find_and_plot_minorcontamination(df_summary, df_titlefile, output_dir, prefix=''):
    patient_normals = {}
    for i, s in df_titlefile.iterrows():
        if s.Class == 'Normal':
            patient_normals[s.Patient_ID] = s.Sample
        else:
            patient_normals[s.Patient_ID] = ''

    minor_contamination = []
    for i, s in df_titlefile.iterrows():
        if s.Class == 'Tumor' and patient_normals[s.Patient_ID] != '':
            minor_contamination.append([s.Sample, df_summary[s.Sample + '_MinorAlleleFreq'][
                df_summary[patient_normals[s.Patient_ID] + '_Genotypes'].isin(['A', 'C', 'G', 'T'])].replace('-',
                                                                                                                 np.nan).astype(
                float).mean()])
        else:
            minor_contamination.append([s.Sample, df_summary[s.Sample + '_MinorAlleleFreq'][
                df_summary[s.Sample + '_Genotypes'].isin(['A', 'C', 'G', 'T'])].replace('-', np.nan).astype(
                float).mean()])

    y_pos = np.arange(len(minor_contamination))
    minor_contamination = sorted(minor_contamination)
    write_csv(output_dir + prefix + 'minorContamination.txt', minor_contamination)

    plt.figure(figsize=(10, 5))
    plt.axhline(y=0.002, xmin=0, xmax=1, c='r', ls='--')
    plt.bar(y_pos, [m[1] for m in minor_contamination], align='center', color='black')
    plt.xticks(y_pos, [m[0] for m in minor_contamination], rotation=90, ha='center')
    plt.ylabel('Avg. Minor Allele Frequency at Homozygous Position')
    plt.xlabel('Sample Name')
    if prefix == 'Duplex':
        plt.title('Minor Contamination Check (Duplex)')
    else:
        plt.title('Minor Contamination Check')
    plt.xlim([-1, y_pos.size])
    plt.savefig(output_dir + '/Minor' + prefix + 'ContaminationRate.pdf', bbox_inches='tight')


def plot_duplex_minor_contamination(waltz_dir_a_duplex, waltz_dir_b_duplex, titlefilepath, config_file, fp_output_dir):
    coverage_thres = 200
    homozygous_thres = 0.05

    # New fp_indices script using pandas
    def create_fp_indices(config_file):
        try:
            config = pd.read_csv(config_file, header=0, sep='\t', dtype=str)
        except FileNotFoundError:
            raise FileNotFoundError('Error: Fingerprinting configure file does not exist')
        # Check if there is a header and remove the header
        if list(config.columns.values) != ['Chrom', 'Pos', 'Allele1', 'Allele2', 'Name'] and list(
                config.columns.values) != ['Chrom', 'Pos', 'Allele1', 'Allele2']:
            raise IOError('Error: Fingerprinting configure file has improper header')
        # Check is there are sites in the file
        if config.shape[0] == 0:
            raise IOError('Error: Fingerprinting configure file is empty')
            # Check is fingerprint has a name and if it doesn't make the name chrom:pos
        if 'Name' not in list(config.columns.values):
            config['Name'] = config['Chrom'] + ':' + config['Pos']
        # Set Index to Chrom:Pos and remove duplicates
        config.index = config['Chrom'] + ':' + config['Pos']
        config.drop_duplicates(inplace=True)
        return config

    # New Extract pileups paths script
    def extract_paired_list_of_pileups(waltz_dir_a_duplex, waltz_dir_b_duplex, listofsamples):
        pairedListOfPileups = []
        for pileupfile in os.listdir(waltz_dir_a_duplex):
            # extract only pileups from Waltz folders
            if pileupfile.endswith("pileup.txt"):
                # Check is file is in the list of Tumor Samples
                samplename = extract_sample_name(pileupfile, titlefile[SAMPLE_ID_COLUMN])
                if samplename in listofsamples:
                    # Check if PoolB pileup exists
                    a_pileup_path = os.path.join(waltz_dir_a_duplex, pileupfile)
                    b_pileup_path = os.path.join(waltz_dir_b_duplex, pileupfile)
                    if os.path.isfile(b_pileup_path):
                        pairedListOfPileups.append([samplename, a_pileup_path, b_pileup_path])
                    else:
                        raise Exception(
                            "Duplex Minor Contamination plot: " + pileupfile + " not found in Duplex Pool B directory provided, " + samplename + " excluded from duplex minor contamination")
        return pairedListOfPileups

    # Make minor contamination rate and all_fp_summary
    def FP_analysis(samplename, fileA, fileB, config):
        a = pd.read_csv(fileA, header=None, sep='\t', dtype=str)
        b = pd.read_csv(fileB, header=None, sep='\t', dtype=str)
        # Merge A and B pileupes
        ab = a.append(b, ignore_index=True)
        ab.drop([8, 9, 10, 11, 12, 13], axis=1, inplace=True)
        ab.columns = ['Chrom', 'Pos', 'Ref', 'Total_Depth', 'A', 'C', 'G', 'T']
        ab.index = ab['Chrom'] + ':' + ab['Pos']
        ab.drop_duplicates(inplace=True)
        # need to check if there is an overlap in bed file and fp_config file
        fp = config.merge(ab)
        allele1_counts = []
        allele2_counts = []
        for i, row in fp.iterrows():
            allele1_counts.append(int(row[row['Allele1']]))
            allele2_counts.append(int(row[row['Allele2']]))
        fp['allele1_count'] = allele1_counts
        fp['allele2_count'] = allele2_counts
        fp['coverage'] = fp[['allele1_count', 'allele2_count']].sum(axis=1)
        # Find Minor allele Fraction of sites with sufficent coverage
        fp.loc[fp.coverage >= coverage_thres, 'mAF'] = fp[['allele1_count', 'allele2_count']].min(axis=1) / fp[
            'coverage']
        # Find Genotype
        fp.loc[fp.mAF > homozygous_thres, 'Geno'] = fp['Allele1'] + fp['Allele2']
        fp.loc[(fp.mAF <= homozygous_thres) & (fp.allele1_count > fp.allele2_count), 'Geno'] = fp['Allele1']
        fp.loc[(fp.mAF <= homozygous_thres) & (fp.allele1_count < fp.allele2_count), 'Geno'] = fp['Allele2']
        # find minor contamination
        minor_contamination = [samplename, fp.loc[fp.mAF <= homozygous_thres, 'mAF'].mean()]
        # Make All_FPsummary file
        fp_summary = pd.DataFrame()
        fp_summary['Locus'] = fp['Chrom'] + ':' + fp['Pos']
        fp_summary[samplename + '_Counts'] = fp['Allele1'] + ':' + fp['allele1_count'].astype(str) + ' ' + fp[
            'Allele2'] + ':' + fp['allele2_count'].astype(str)
        fp_summary[samplename + '_Genotypes'] = fp['Geno']
        fp_summary[samplename + '_MinorAlleleFreq'] = fp['mAF']
        fp_summary.fillna(value='-', inplace=True)
        return minor_contamination, fp_summary

    # RUN
    titlefile = read_df(titlefilepath, header='infer')
    listofsamples = titlefile.loc[titlefile[TITLE_FILE__SAMPLE_CLASS_COLUMN] == 'Tumor'][SAMPLE_ID_COLUMN].tolist()
    config = create_fp_indices(config_file)
    # Check if Waltz Directories exist
    if not (os.path.isdir(waltz_dir_a_duplex) and os.path.isdir(waltz_dir_b_duplex)):
        raise IOError(
            'Error: One or both of the input directory with pileups provided to plot_duplex_minor_contamination does not exist')
        # Check if there are any tumor samples in this Run
    if not listofsamples:
        logging.warn("Duplex Minor Contamination plot: No Samples marked as Tumor in Titlefile")
        return
    # Extract paired pileup files
    pairedListOfPileups = extract_paired_list_of_pileups(waltz_dir_a_duplex, waltz_dir_b_duplex, listofsamples)
    for i, [samplename, fileA, fileB] in enumerate(pairedListOfPileups):
        if i == 0:
            minor_contamination, all_fp_summary = FP_analysis(samplename, fileA, fileB, config)
            all_minor_contamination = [minor_contamination]
        else:
            minor_contamination, fp_summary = FP_analysis(samplename, fileA, fileB, config)
            all_minor_contamination.append(minor_contamination)
            all_fp_summary = all_fp_summary.merge(fp_summary, on='Locus')
    # Reorder snps
    all_fp_summary.set_index('Locus', inplace=True)
    index = all_fp_summary.index.tolist()
    index = natural_sort(index)
    all_fp_summary = all_fp_summary.reindex(index)
    # print summary
    all_fp_summary.to_csv(fp_output_dir + '/duplex_ALL_FPsummary.txt', sep="\t", index=True)
    # plot minor contamination
    all_minor_contamination = [x for x in all_minor_contamination if not np.isnan(x[1])]
    all_minor_contamination = sorted(all_minor_contamination)
    df_minor_contamination = pd.DataFrame(all_minor_contamination,
                                          columns=['SampleName', 'MinorContaminationRateInDuplex'])
    df_minor_contamination.to_csv(fp_output_dir + '/duplex_minor_contamination.txt', sep="\t", index=False)

    plt.clf()
    y_pos = np.arange(len(all_minor_contamination))
    plt.figure(figsize=(10, 5), facecolor='white')
    plt.axhline(y=0.002, xmin=0, xmax=1, c='r', ls='--')
    plt.bar(y_pos, [m[1] for m in all_minor_contamination], align='center', color='black')
    plt.xticks(y_pos, [m[0] for m in all_minor_contamination], rotation=90, ha='center')
    plt.ylabel('Avg. Minor Allele Frequency at Homozygous Position')
    plt.xlabel('Sample Name')
    plt.title('Minor Contamination Check (Duplex)')
    plt.xlim([-1, y_pos.size])
    # plt.autoscale(True)
    plt.tick_params(top='off', bottom='on', left='on', right='off', labelleft='on', labelbottom='on')
    try:
        plt.ylim([0, max([.0021, max([a[1] for a in all_minor_contamination]) + .0005])])
    except ValueError:
        # no minor allele values for test data
        print("Error while plotting fingerprinting.")
        pass
    plt.savefig(fp_output_dir + '/MinorDuplexContaminationRate.pdf', bbox_inches='tight')



def plot_genotyping_matrix(geno_compare, fp_output_dir, title_file):
    plt.clf()
    if geno_compare[0][0] == "ReferenceSample":
        geno_compare = geno_compare[1::]

    hm_compare = [[g[0], g[1], g[8]] for g in geno_compare]

    if len(hm_compare) == 0:
        # Only had one sample, and thus no comparisons to make
        titlefile = pd.read_csv(title_file, sep='\t')
        sample = titlefile[TITLE_FILE__SAMPLE_ID_COLUMN].values[0]
        hm_compare = [[sample, sample, 0]]

    matrix = {}

    for element in hm_compare:
        if element[0] not in matrix.keys():
            matrix[element[0]] = {element[1]: element[2]}
        matrix[element[0]].update({element[1]: element[2]})

    # Just print matrix of 0's when testing
    discordance_data_frame = pd.DataFrame.from_dict(matrix)
    if discordance_data_frame.isnull().all().all():
        discordance_data_frame[:] = 0

    plt.subplots(figsize=(8, 7))
    plt.title('Sample Mix-Ups')
    # print(matrix)
    sns.set(font_scale=.6)
    try:
        ax = sns.heatmap(discordance_data_frame.astype(float), robust=True, xticklabels=True, yticklabels=True, annot=False,
                        fmt='.2f', cmap="Blues_r", vmax=.15,
                        cbar_kws={'label': 'Fraction Mismatch'},
                        annot_kws={'size': 5})
        # This sets the yticks "upright" with 0, as opposed to sideways with 90.
        plt.yticks(rotation=0) 
    except IndexError:
        # No mismatch values for test data is possible
        print("NaN fraction mismatch values for all samples.")
        pass

    plt.savefig(fp_output_dir + 'GenoMatrix.pdf', bbox_inches='tight')

    Match_status = [[x[0], x[1], x[9]] for x in geno_compare if
                    x[9] == 'Unexpected Mismatch' or x[9] == 'Unexpected Match']

    # Deduplicate forward and reverse matches
    Match_status = [sorted([match[0], match[1]]) + [match[2]] for match in Match_status]
    Match_status = list(match for match, _ in itertools.groupby(Match_status))

    df = pd.DataFrame(Match_status, columns=['Sample1', 'Sample2', 'Status'])

    df[(df['Status'] == 'Unexpected Mismatch') & (~df['Sample1'].str.contains(CONTROL_SAMPLE_KEYWORD)) & (~df['Sample2'].str.contains(CONTROL_SAMPLE_KEYWORD))].to_csv(fp_output_dir + 'UnexpectedMismatch.txt', sep='\t', index=False)
    df[(df['Status'] == 'Unexpected Match') & (~df['Sample1'].str.contains(CONTROL_SAMPLE_KEYWORD)) & (~df['Sample2'].str.contains(CONTROL_SAMPLE_KEYWORD))].to_csv(fp_output_dir + 'UnexpectedMatch.txt', sep='\t', index=False)

    plt.clf()
    fig, ax1 = plt.subplots()
    fig.set_figheight(1)
    fig.suptitle('Unexpected Matches', fontsize=10, y=.5)
    ax1.axis('off')
    ax1.axis('tight')
    if len(df[df['Status'] == 'Unexpected Match'].values):
        ax1.table(cellText=df[df['Status'] == 'Unexpected Match'].values, colLabels=df.columns, loc='bottom',
                  cellLoc='center', rowLoc='center')
    else:
        empty_values = [['No unexpected matches present', 'No unexpected matches present', 'No mismatches present']]
        ax1.table(cellText=empty_values, colLabels=df.columns, loc='bottom')
    fig.tight_layout()

    plt.savefig(fp_output_dir + 'Unexpected_Match.pdf', bbox_inches='tight')

    plt.clf()
    fig, ax1 = plt.subplots()
    fig.set_figheight(1)
    fig.suptitle('Unexpected Mismatches', fontsize=10, y=.5)
    ax1.axis('off')
    ax1.axis('tight')
    if len(df[df['Status'] == 'Unexpected Mismatch'].values):
        ax1.table(cellText=df[df['Status'] == 'Unexpected Mismatch'].values, colLabels=df.columns, loc='bottom',
                  cellLoc='center', rowLoc='center')
    else:
        empty_values = [['No unexpected mismatches present', 'No unexpected mismatches present',
                         'No unexpected mismatches present']]
        ax1.table(cellText=empty_values, colLabels=df.columns, loc='bottom')
    fig.tight_layout()
    plt.savefig(fp_output_dir + 'Unexpected_Mismatch.pdf', bbox_inches='tight')



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

    df = pd.DataFrame(mismatch_sex, columns=[TITLE_FILE__SAMPLE_ID_COLUMN, "Reported Sex", "Inferred Sex"])
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
# Reformat fingerprinting output for Clinical database integration
######################

def reformat_all(listofpileups, fp_indices, fp_output_dir):
    def FP_reformat(pileupfile, fp_indices):
        # Per Sample

        # Constants
        alleleReverseInd = {4: 'A', 5: 'C', 6: 'G', 7: 'T'}
        alleles = ['A', 'C', 'G', 'T']
        # Parameter
        thres = 0.1  # heterozygous above this threshold
        # Get Raw data

        pileup = read_csv(pileupfile)
        fpRaw = []
        for p in pileup:
            if p[0] + ':' + p[1] in fp_indices.keys() and p[0] + ':' + p[1] not in [f[0] + ':' + f[1] for f in fpRaw]:
                fpRaw.append(p[0:8])
        # Create Header
        # TODO: consider changing this to pull samplename from title file
        samplename = os.path.basename(pileupfile).split("_cl")[0]
        reformatted_sample = [
            ['Locus', samplename + '_Counts', samplename + '_Genotypes', samplename + '_MinorAlleleFreq']]
        # Calculate and Reformat Data
        for eachfp in fpRaw:
            idx = eachfp[0] + ':' + eachfp[1]
            line = fp_indices[idx]

            loc_allele1 = line[0]
            loc_allele2 = line[1]

            count_allele1 = eachfp[loc_allele1]
            count_allele2 = eachfp[loc_allele2]
            counts = [int(count_allele1), int(count_allele2)]

            mAF = min(counts) / sum(counts) if sum(counts) != 0 else 999

            Geno = alleles[np.argmax([int(F) for F in eachfp[4::]])] if mAF <= thres else '-' if mAF == 999 else \
            alleleReverseInd[loc_allele1] + alleleReverseInd[loc_allele2]

            mAF = '-' if mAF == 999 else mAF

            reformatted_sample.append([idx, alleleReverseInd[loc_allele1] + ':' + eachfp[loc_allele1] + ' ' +
                                       alleleReverseInd[loc_allele2] + ':' + eachfp[loc_allele2], Geno, mAF])
        df_reformated_sample = pd.DataFrame(reformatted_sample[1:], columns=reformatted_sample[0])
        return df_reformated_sample

    # loop for all samples
    for i, pileupfile in enumerate(listofpileups):
        if i == 0:
            all_reformatted = FP_reformat(pileupfile, fp_indices)
        else:
            df_reformatted_sample = FP_reformat(pileupfile, fp_indices)
            all_reformatted = all_reformatted.merge(df_reformatted_sample, on='Locus')

    # do natural sort
    all_reformatted.set_index('Locus', inplace=True)
    index = all_reformatted.index.tolist()
    index = natural_sort(index)
    all_reformatted = all_reformatted.reindex(index)

    # save to file
    all_reformatted.to_csv(fp_output_dir + '/ALL_FPsummary.txt', sep="\t", index=True)
    return all_reformatted



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
    
    # reformat for clinical database    
    reformat_all(listofpileups, fp_indices, fp_output_dir)

    # reformat for clinical database
    all_reformatted = reformat_all(listofpileups, fp_indices, fp_output_dir)

    # Contamination plots
    df_titlefile = read_df(titlefile, header='infer')
    find_and_plot_minorcontamination(all_reformatted, df_titlefile, fp_output_dir, prefix='')
    ##plot_minor_contamination(all_fp, fp_output_dir, titlefile)

    plot_major_contamination(all_geno, fp_output_dir, titlefile)

    # plotGenoCompare(geno_compare,n, fpOutputdir)
    geno_compare = compare_genotype(all_geno, n, fp_output_dir, titlefile)
    plot_genotyping_matrix(geno_compare, fp_output_dir, titlefile)

    # Duplex Plot
    plot_duplex_minor_contamination(waltz_dir_a_duplex, waltz_dir_b_duplex, titlefile, config_file, fp_output_dir)

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
