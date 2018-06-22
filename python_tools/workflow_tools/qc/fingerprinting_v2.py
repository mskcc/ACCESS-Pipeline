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
import os
import numpy as np
import argparse
import pandas as pd
from PyPDF2 import PdfFileMerger

import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns

from ...util import extract_sample_name, read_df
from ...constants import *


###################
##Helper Functions
###################

def readCVS(filename):
    data = []
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            data.append(row)
    return data


def writeCVS(filename, data):
    with open(filename, 'a') as f:
        writer = csv.writer(f, delimiter='\t')
        for row in data:
            writer.writerow(row)


def mergePdfInFolder(inDir, outDir, filename):
    merger = PdfFileMerger()

    pdfs = [x for x in os.listdir(outDir) if '.pdf' in x]
    pdfs.sort()
    if len(pdfs) > 1:
        for pdf in pdfs:
            merger.append(open(outDir + pdf, 'rb'))

        with open(outDir + 'FPFigures.pdf', 'wb') as fout:
            merger.write(fout)
    else:
        raise IOError('Error: ' + filename + ' not created, input folder does not have PDFs to merge')


def MakeOutputDir(OutputDir, DirName):
    if os.path.exists(OutputDir):
        if os.path.exists(OutputDir + '/' + DirName):
            raise IOError(
                'Error ' + DirName + ' already exist in the OutputDir, either remove or rename Older directory')
        else:
            os.mkdir(OutputDir + '/' + DirName)
            return OutputDir + '/' + DirName + '/'
    else:
        raise IOError('Error: Output directory does not exist')


###################
##Extract RawData Functions
###################
def Extractpileupfiles(InputDir):
    listofpileups = []
    if os.path.isdir(InputDir):
        for pileupfile in os.listdir(InputDir):
            if pileupfile.endswith("pileup.txt"):
                listofpileups.append(InputDir + '/' + pileupfile)
        return listofpileups
    else:
        raise IOError('Error: Input Directory with pileups does not exist')


def createFPIndices(configFile):
    # Import config file.
    try:
        config = readCVS(configFile)
    except IOError:
        raise IOError('Error: FP configure file does not exist')
    # Check if there is a header and remove the header
    if config[0][0].lower() != 'Chrom'.lower():
        raise IOError('Error: FP configure has improper header')
    else:
        # Remove header and make index
        config.pop(0)
        fpIndices = dict()
        alleleInd = {'A': 4, 'C': 5, 'G': 6, 'T': 7}
        # Convert to Dict
        for f in config:
            if len(f) == 4:
                fpIndices[f[0] + ':' + f[1]] = [alleleInd[f[2]], alleleInd[f[3]], f[0] + ':' + f[1]]
            elif len(f) == 5:
                fpIndices[f[0] + ':' + f[1]] = [alleleInd[f[2]], alleleInd[f[3]], f[4]]
        n = len(fpIndices.keys())
        return fpIndices, n


def ExtractListofTumorSamples(titlefile):
    title = readCVS(titlefile)
    listofsamples = [t[2].replace('_', '-') for i, t in enumerate(title) if t[5] == "Tumor"]
    return listofsamples


def concatenate_AandB_pileups(WaltzDirA, WaltzDirB, OutputDir, DirName, listofsamples=[]):
    MergedDir = MakeOutputDir(OutputDir, DirName)
    listofpileups = [p for p in os.listdir(WaltzDirA) if p.endswith("-pileup.txt")]
    # Added: If you want to concatenate only some of the samples (i.e. Only Tumor Samples)
    if listofsamples:
        newlistofpileups = []
        for s in listofsamples:
            for p in listofpileups:
                if p.startswith(s):
                    newlistofpileups.append(p)
        listofpileups = newlistofpileups

    for p in listofpileups:
        if p in os.listdir(WaltzDirB):
            a = readCVS(WaltzDirA + '/' + p)
            b = readCVS(WaltzDirB + '/' + p)
            a.extend(b)
            # this is not a uniq list. extractRawFP makes sure FP pileups are unique.
            writeCVS(MergedDir + '/' + p, a)
        else:
            raise IOError(p + " not in WaltzDirB so pileup not concatenated and sample not fingerprinted")
    return MergedDir


###################
##Run Analysis
###################
def extractRawFP(pileupfile, fpIndices):
    pileup = readCVS(pileupfile)
    fpRaw = []
    for p in pileup:
        if p[0] + ':' + p[1] in fpIndices.keys() and p[0] + ':' + p[1] not in [f[0] + ':' + f[1] for f in fpRaw]:
            fpRaw.append(p[0:8])
    name = os.path.basename(pileupfile)
    fpRaw.insert(0, [name])
    return fpRaw


def FindFPMAF(listofpileups, fpIndices, fpOutputdir):
    All_FP = []
    All_geno = []
    Alleles = ['A', 'C', 'G', 'T']
    thres = 0.1
    for pileupfile in listofpileups:
        fpRaw = extractRawFP(pileupfile, fpIndices)
        # writeCVS (fpOutputdir+'FP_counts.txt', fpRaw)
        name = fpRaw.pop(0)
        if All_FP == []:
            header = [fpIndices[eachfp[0] + ':' + eachfp[1]][2] for eachfp in fpRaw]
            header.insert(0, 'Sample')
            All_FP.append(header)
            All_geno.append(header)
        FPmAF = [min(counts) / sum(counts) if sum(counts) != 0 else 999 for counts in
                 [[int(eachfp[index]) for index in fpIndices[eachfp[0] + ':' + eachfp[1]][0:2]] for eachfp in fpRaw]]
        FPGeno = [Alleles[np.argmax([int(F) for F in f[4::]])] if FPmAF[i] <= thres else "Het" for i, f in
                  enumerate(fpRaw)]
        FPmAF.insert(0, name[0])
        FPGeno.insert(0, name[0])
        All_FP.append(FPmAF)
        All_geno.append(FPGeno)
        for p in fpRaw:
            p.insert(0, name[0])
        writeCVS(fpOutputdir + 'FP_counts.txt', fpRaw)
    writeCVS(fpOutputdir + 'FP_mAF.txt', All_FP)
    writeCVS(fpOutputdir + 'FP_Geno.txt', All_geno)
    return All_FP, All_geno


def ContaminationRate(All_FP):
    contamination = []
    All_FP = All_FP[1::]
    for sample in All_FP:
        homozygous = [x for x in sample[1::] if x <= .1]
        if len(homozygous) != 0:
            contamination.append([sample[0], np.mean(homozygous)])
        else:
            contamination.append([sample[0], 'NaN'])
    return contamination


def createExpectedFile(titlefile, fpOutputdir):
    title = readCVS(titlefile)
    samples = [t[2:5] for t in title]
    samples.pop(0)

    patient = {}

    for s in samples:
        if s[2] in patient.keys():
            patient[s[2]].append(s[0])
        else:
            patient[s[2]] = [s[0]]

    expected = []
    for key, samples_per_patient in patient.items():
        if len(samples_per_patient) == 2:
            expected.append(samples_per_patient)
        elif len(samples_per_patient) > 2:
            for i, s1 in enumerate(samples_per_patient):
                for s2 in samples_per_patient[i + 1::]:
                    expected.append([s1, s2])
    if expected:
        writeCVS(fpOutputdir + '/ExpectedMatches.txt', expected)
    return expected


def compare_genotype(All_geno, n, fpOutputdir, titlefile):
    expected = createExpectedFile(titlefile, fpOutputdir)
    titlefile = read_df(titlefile, header='infer')

    if All_geno[0][0] == 'Sample':
        All_geno = All_geno[1::]

    All_geno = [a for a in All_geno if 'CELLFREEPOOLEDNORMAL' not in a[0]]
    Geno_Compare = []
    for i, g in enumerate(All_geno):
        for h in All_geno[i + 1::]:
            hmMatch = 0
            hmMisMatch = 0
            htMatch = 0
            htMisMatch = 0
            TotalMatch = 0
            for j, element in enumerate(g):
                if element == h[j]:
                    TotalMatch = TotalMatch + 1
                    if element == 'Het':
                        htMatch = htMatch + 1
                    else:
                        hmMatch = hmMatch + 1
                elif element == 'Het' or h[j] == 'Het':
                    htMisMatch = htMisMatch + 1
                elif j != 0:
                    hmMisMatch = hmMisMatch + 1

            # Todo: Use util.extract_sample_name() instead of relying on "IGO"
            # Geno_Compare.append([g[0][0:g[0].find('_bc')],h[0][0:h[0].find('_bc')], TotalMatch, hmMatch, hmMisMatch, htMatch, htMisMatch])
            # Geno_Compare.append([g[0][0:g[0].find('[-_]IGO')],h[0][0:h[0].find('[-_]IGO')], TotalMatch, hmMatch, hmMisMatch, htMatch, htMisMatch])
            sample_g = extract_sample_name(g[0], titlefile[TITLE_FILE__SAMPLE_ID_COLUMN])
            sample_h = extract_sample_name(h[0], titlefile[TITLE_FILE__SAMPLE_ID_COLUMN])
            Geno_Compare.append([sample_g, sample_h, TotalMatch, hmMatch, hmMisMatch, htMatch, htMisMatch])

    sort_index = np.argsort([x[2] for x in Geno_Compare])
    Geno_Compare = [Geno_Compare[i] for i in sort_index]

    # mlist=[i for i, x in enumerate([g[2] for g in Geno_Compare]) if x/n>.8] #Total Match/All Fingerprinting snps
    mlist = [i for i, x in enumerate([[int(g[4]), int(g[3]) + int(g[4])] for g in Geno_Compare]) if
             x[0] / (x[1] + EPSILON) < .1]  # Homozygous Mismatch/All Homozygous SNPs
    if mlist != []:
        m = min(mlist)
    else:
        m = len(Geno_Compare)
    expectedInd = []
    for y in expected:
        for i, x in enumerate(Geno_Compare):
            if [x[0], x[1]] == y or [x[1], x[0]] == y:
                expectedInd.append(i)
    for i, x in enumerate(Geno_Compare):
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
    Geno_Compare.insert(0, ["Sample1", "Sample2", "TotalMatch", "HomozygousMatch", "HomozygousMismatch",
                            "HeteozygousMatch", "HeteozygousMismatch", "Status"])
    writeCVS(fpOutputdir + 'Geno_compare.txt', Geno_Compare)
    return Geno_Compare


###################
##Plot Functions
###################

def plotMinorContamination(All_FP, fpOutputdir, titlefile):
    plt.clf()
    contamination = ContaminationRate(All_FP)
    contamination = [x for x in contamination if x[1] != 'NaN']
    titlefile = read_df(titlefile, header='infer')
    samplename = [extract_sample_name(c[0], titlefile[TITLE_FILE__SAMPLE_ID_COLUMN]) for c in contamination]
    y_pos = np.arange(len(samplename))
    meanContam = [c[1] for c in contamination]
    minorContamination = [[samplename[i], meanContam[i]] for i in range(0, len(samplename))]
    minorContamination = sorted(minorContamination)
    writeCVS(fpOutputdir + 'minorContamination.txt', minorContamination)

    plt.figure(figsize=(10, 5))
    plt.axhline(y=0.005, xmin=0, xmax=1, c='r', ls='--')
    plt.bar(y_pos, [m[1] for m in minorContamination], align='edge', color='black')
    plt.xticks(y_pos, [m[0] for m in minorContamination], rotation=90, ha='left')
    plt.ylabel('Avg. Minor Allele Frequency at Homozygous Position')
    plt.xlabel('Sample Name')
    plt.title('Minor Contamination Check (from all reads)')
    plt.xlim([0, y_pos.size])
    plt.savefig(fpOutputdir + '/MinorContaminationRate.pdf', bbox_inches='tight')


def plotMajorContamination(All_geno, fpOutputdir, titlefile):
    plt.clf()
    if All_geno[0][0] == 'Sample':
        All_geno = All_geno[1::]
    titlefile = read_df(titlefile, header='infer')
    samples = [extract_sample_name(g[0], titlefile[TITLE_FILE__SAMPLE_ID_COLUMN]) for g in All_geno]
    x_pos = np.arange(len(All_geno))
    pHet = [sum([1 for a in g if a == 'Het']) / (len(g) - 1) for g in All_geno]

    majorContamination = [[samples[i], pHet[i]] for i in range(0, len(samples))]
    majorContamination = sorted(majorContamination)
    writeCVS(fpOutputdir + 'majorContamination.txt', majorContamination)

    plt.axhline(y=0.55, xmin=0, xmax=1, c='r', ls='--')
    plt.bar(x_pos, [m[1] for m in majorContamination], align='edge', color='black')
    plt.xticks(x_pos, [m[0] for m in majorContamination], rotation=90, ha='left')
    plt.ylabel('% of Heterozygous Position')
    plt.xlabel('Sample Name')
    plt.title('Major Contamination Check')
    plt.xlim([0, x_pos.size])
    plt.savefig(fpOutputdir + 'MajorContaminationRate.pdf', bbox_inches='tight')


def plotduplexMinorContamination(WaltzDirA_duplex, WaltzDirB_duplex, titlefile, OutputDir, fpIndices, fpOutputdir):
    listofsamples = ExtractListofTumorSamples(titlefile)
    if listofsamples:
        duplexMergedDir = concatenate_AandB_pileups(WaltzDirA_duplex, WaltzDirB_duplex, OutputDir, 'DuplexMergedPileup',
                                                    listofsamples)
        fpDuplexOutputdir = MakeOutputDir(fpOutputdir, 'FPDuplexResults')
        listofduplexpileups = Extractpileupfiles(duplexMergedDir)
        All_FP, All_geno = FindFPMAF(listofduplexpileups, fpIndices, fpDuplexOutputdir)
        # Plot the Contamination
        plt.clf()
        contamination = ContaminationRate(All_FP)
        contamination = [x for x in contamination if x[1] != 'NaN']
        ##To Do: Find the samplename from titlefile
        samplename = [c[0][0:c[0].find('IGO')] for c in contamination]

        title_file = read_df(titlefile, header='infer')
        samplename = [extract_sample_name(s, title_file[TITLE_FILE__SAMPLE_ID_COLUMN]) for s in samplename]

        y_pos = np.arange(len(samplename))
        meanContam = [c[1] for c in contamination]
        minorContamination = [[samplename[i], meanContam[i]] for i in range(0, len(samplename))]
        minorContamination = sorted(minorContamination)
        writeCVS(fpOutputdir + 'minorDuplexContamination.txt', minorContamination)

        plt.figure(figsize=(10, 5))
        plt.axhline(y=0.02, xmin=0, xmax=1, c='r', ls='--')
        plt.axhline(y=0.01, xmin=0, xmax=1, c='orange', ls='--')
        plt.bar(y_pos, [m[1] for m in minorContamination], align='edge', color='black')
        plt.xticks(y_pos, [m[0] for m in minorContamination], rotation=90, ha='left')
        plt.ylabel('Avg. Minor Allele Frequency at Homozygous Position')
        plt.xlabel('Sample Name')
        plt.title('Minor Contamination Check (Duplex)')
        plt.xlim([0, y_pos.size])
        plt.savefig(fpOutputdir + '/MinorDuplexContaminationRate.pdf', bbox_inches='tight')
    else:
        print("Duplex Minor Contamination plot: No Samples marked as Tumor in Titlefile")


def plotGenoCompare(Geno_Compare, n, fpOutputdir):
    plt.clf()
    if Geno_Compare[0][0] == "Sample1":
        Geno_Compare = Geno_Compare[1::]
    Geno_Compare = [x for x in Geno_Compare if x[7] != 'Expected Mismatch']
    if Geno_Compare:
        samples = [c[0] + ' : ' + c[1] for c in Geno_Compare]
        y_pos = np.arange(len(Geno_Compare))
        plt.figure(figsize=(5, 5))
        for i, g in enumerate(Geno_Compare):
            if g[7] == 'Unexpected Match':
                plt.axhspan(i, i + 1, facecolor='.5', alpha=0.5)
        plt.axvline(x=0, ymin=0, ymax=1, c='black', ls='-', linewidth=2)
        plt.axvline(x=0.8, ymin=0, ymax=1, c='black', ls='--')
        newmlist = [i for i, x in enumerate([g[2] for g in Geno_Compare]) if x / n > .8]
        if newmlist:
            newm = min(newmlist)
            plt.axhline(y=newm - .15, xmin=0, xmax=1, c='red', ls=':', linewidth=3)
        plt.barh(y_pos, [(g[3] + g[5]) / n for g in Geno_Compare], align='edge', color='#ff9b9b', alpha=0.5,
                 label='Matched Homozygous')
        plt.barh(y_pos, [g[5] / n for g in Geno_Compare], align='edge', color='#b9d6c8', label='Matched Heterozygous')
        plt.barh(y_pos, [(-g[4] - g[6]) / n for g in Geno_Compare], align='edge', color='#d1909c',
                 label='Mismatched Homozygous')
        plt.barh(y_pos, [-g[6] / n for g in Geno_Compare], align='edge', color='#7f9990',
                 label='Mismatched Heterozygous')
        plt.yticks(y_pos, samples, va='bottom')
        plt.axes().yaxis.grid()

        plt.legend(bbox_to_anchor=(1.8, 0.5))
        plt.xlabel('Fingerprint Comparision')
        plt.ylabel('Samples Compared')
        plt.title('Fraction of Matching Fingerprints', fontsize=16)
        plt.savefig(fpOutputdir + 'Selectfpcompare.pdf', bbox_inches='tight')


def plotGenotypingMatrix(Geno_Compare, fpOutputdir):
    plt.clf()
    if Geno_Compare[0][0] == "Sample1":
        Geno_Compare = Geno_Compare[1::]
    ## Note: that if the coverage in all Homozygous Sites is less the 10 (failed sample), the mismatch rate is defaulted to 1.
    hm_compare = [[g[0], g[1], int(g[4]) / (int(g[3]) + int(g[4])) if (int(g[3]) + int(g[4])) > 10 else 1] for g in
                  Geno_Compare]
    matrix = {}

    for element in hm_compare:
        if element[0] not in matrix.keys():
            matrix[element[0]] = {}
        if element[1] not in matrix.keys():
            matrix[element[1]] = {}
        matrix[element[0]].update({element[0]: 0, element[1]: element[2]})
        matrix[element[1]].update({element[1]: 0, element[0]: element[2]})

    keys = sorted([k for k in matrix.keys()])
    listMatrix = [[matrix[k1][k2] for k2 in keys] for k1 in keys]

    plt.subplots(figsize=(8, 7))
    plt.title('Sample Mix-Ups')
    ax = sns.heatmap(listMatrix, robust=True, fmt='f', cmap="Blues_r", vmax=.25,
                     cbar_kws={'label': 'Fraction Mismatch Homozygous'})
    ax.set_xticklabels(keys, rotation=90, fontsize=11)
    ax.set_yticklabels(keys, rotation=0, fontsize=11)
    # ax.set_yticklabels(keys[::-1], rotation=0,fontsize=11)
    plt.savefig(fpOutputdir + 'GenoMatrix.pdf', bbox_inches='tight')

    Match_status = [[x[0], x[1], x[7]] for x in Geno_Compare if
                    x[7] == 'Unexpected Mismatch' or x[7] == 'Unexpected Match']

    df = pd.DataFrame(Match_status, columns=["Sample1", "Sample2", "Status"])
    Match_status.insert(0, ["Sample1", "Sample2", "Status"])
    writeCVS(fpOutputdir + 'Match_status.txt', Match_status)

    plt.clf()
    fig, ax1 = plt.subplots()
    # plt.title('Unexpected Matches and Mismatches')
    ax1.axis('off')
    ax1.axis('tight')
    if len(df.values):
        ax1.table(cellText=df.values, colLabels=df.columns, loc='center')
    else:
        empty_values = [['No mismatches present', 'No mismatches present', 'No mismatches present']]
        ax1.table(cellText=empty_values, colLabels=df.columns, loc='center')
    fig.tight_layout()
    plt.savefig(fpOutputdir + 'Geno_Match_status.pdf', bbox_inches='tight')


def FindSexFromPileup(WaltzDir, OutputDir):
    # Not Currently Used: Checks the pileups if there are more that 200 positions in the Y chromosome with at least 1 read, the sample is classified as male.
    sex = []
    for file in os.listdir(WaltzDir):
        if file[-10::] == 'pileup.txt':
            data = []
            with open(WaltzDir + '/' + file, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                for row in reader:
                    if row[0] == 'Y':
                        if int(row[3]) > 0:
                            data.append(row[3])

            if len(data) > 200:
                sex.append([file[0:file.find('_bc')], "Male"])
            else:
                sex.append([file[0:file.find('_bc')], "Female"])
    writeCVS(OutputDir + '/Sample_sex_from_pileup.txt', sex)
    return sex


def FindSexFromInterval(WaltzDir, OutputDir):
    # Used: Checks the Interval files if the sum of the average coverage per interval (2 on Y) is greater that 50, the sample is classified as male.
    sex = []
    for file in os.listdir(WaltzDir):
        if file[-13::] == 'intervals.txt':
            data = []
            with open(WaltzDir + '/' + file, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                for row in reader:
                    if row[3] == 'Tiling_SRY_Y:2655301' or row[3] == 'Tiling_USP9Y_Y:14891501':
                        data.append(row[5])

            if sum(data) > 50:
                sex.append([file[0:file.find('_bc')], "Male"])
            else:
                sex.append([file[0:file.find('_bc')], "Female"])
    writeCVS(OutputDir + '/Sample_sex_from_pileup.txt', sex)
    return sex


def standardizeGender(titleFile):
    ##Potential inputs
    female = ['female', 'f', 'Female', 'F']
    male = ['Male', 'M', 'male', 'm']
    ##
    titleInfo = readCVS(titleFile)
    gender_from_title = [[t[2], t[11]] for t in titleInfo]
    gender = []
    for s in gender_from_title:
        if s[1] in female:
            gender.append([s[0].replace('_', '-'), 'Female'])
        elif s[1] in male:
            gender.append([s[0].replace('_', '-'), 'Male'])
    return gender


def CheckSex(gender, sex, OutputDir):
    list_of_samples = [s[0] for s in sex]
    MisMatchSex = []
    for g in gender:
        if g[0] in list_of_samples:
            idx = list_of_samples.index(g[0])
            if g[1] != sex[idx][1]:
                MisMatchSex.append([g[0], g[1], sex[idx][1]])
    if MisMatchSex:
        df = pd.DataFrame(MisMatchSex, columns=["Sample", "GenderFromTitleFile", "SexFromPileup"])
        writeCVS(OutputDir + '/MisMatchedGender.txt', MisMatchSex)
        plt.clf()
        fig, ax = plt.subplots()
        plt.title('Gender MisMatch')
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, colLabels=df.columns, loc='center')
        fig.tight_layout()
        plt.savefig(OutputDir + '/GenderMisMatch.pdf', bbox_inches='tight')


######################
# Convert Txt files
######################

def convertFP_mAF(InputDir, OutputDir):
    x = readCVS(InputDir + 'FP_mAF.txt')
    All_FP = []
    for sample in x[1::]:
        new = [float(i) for i in sample[1::]]
        new.insert(0, sample[0])
        All_FP.append(new)
    All_FP.insert(0, x[0])
    return All_FP


######################
# Main Function
######################

def runFPreport(OutputDir, WaltzDirA, WaltzDirB, WaltzDirA_duplex, WaltzDirB_duplex, configFile, titlefile):
    mergedDir = concatenate_AandB_pileups(WaltzDirA, WaltzDirB, OutputDir, 'MergedPileup')
    listofpileups = Extractpileupfiles(mergedDir)
    fpIndices, n = createFPIndices(configFile)
    fpOutputdir = MakeOutputDir(OutputDir, 'FPResults')
    All_FP, All_geno = FindFPMAF(listofpileups, fpIndices, fpOutputdir)
    Geno_Compare = compare_genotype(All_geno, n, fpOutputdir, titlefile)
    # plots
    plotMinorContamination(All_FP, fpOutputdir, titlefile)
    plotMajorContamination(All_geno, fpOutputdir, titlefile)
    # plotGenoCompare (Geno_Compare,n, fpOutputdir)
    plotGenotypingMatrix(Geno_Compare, fpOutputdir)
    # Duplex Plot
    listofsamples = ExtractListofTumorSamples(titlefile)
    plotduplexMinorContamination(WaltzDirA_duplex, WaltzDirB_duplex, titlefile, OutputDir, fpIndices, fpOutputdir)
    mergePdfInFolder(fpOutputdir, fpOutputdir, 'FPFigures.pdf')
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
    runFPreport(OutputDir=args.output_dir, WaltzDirA=args.waltz_dir_A, WaltzDirB=args.waltz_dir_B,
                WaltzDirA_duplex=args.waltz_dir_A_duplex, WaltzDirB_duplex=args.waltz_dir_B_duplex,
                configFile=args.fp_config, titlefile=args.title_file)

    # Sex
    sex=FindSexFromInterval(WaltzDir=args.waltz_dir, OutputDir=args.output_dir)
    gender=standardizeGender(titleFile=args.title_file)
    CheckSex(gender, sex, OutputDir=args.output_dir)


if __name__ == '__main__':
    main()
