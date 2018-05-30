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
from PyPDF2 import PdfFileMerger

import matplotlib
matplotlib.use('PDF')
import matplotlib.pyplot as plt


###################
##Helper Functions
###################

def readCVS (filename):
  data = []
  with open(filename, 'r') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
      data.append(row)
  return data

def writeCVS (filename, data):
  with open(filename, 'a') as f:
    writer = csv.writer(f, delimiter='\t')
    for row in data:
        writer.writerow(row)

def mergePdfInFolder(inDir, outDir, filename):
    merger = PdfFileMerger()

    pdfs=[x for x in os.listdir(outDir) if '.pdf' in x]
    if len(pdfs)>1:
        for pdf in pdfs:
            merger.append(open(outDir+pdf, 'rb'))

        with open(outDir+'FPFigures.pdf', 'wb') as fout:
            merger.write(fout)
    else:
        raise IOError('Error: '+filename+' not created, input folder does not have PDFs to merge')


###################
##Extract RawData Functions
###################
def Extractpileupfiles (WaltzDir):
    listofpileups=[]
    if os.path.isdir(WaltzDir):
        for pileupfile in os.listdir(WaltzDir):
            if pileupfile.endswith("pileup.txt"):
                listofpileups.append(WaltzDir+'/'+pileupfile)
        return listofpileups
    else:
        raise IOError('Error: Waltz Directory does not exist')


def createFPIndices(configFile):
    #Import config file.
    try:
        config=readCVS(configFile)
    except IOError:
        raise IOError('Error: FP configure file does not exist')
    #Check if there is a header and remove the header
    if config[0][0].lower()!='Chrom'.lower():
        raise IOError('Error: FP configure has improper header')
    else:
        #Remove header and make index
        config.pop(0)
        fpIndices=dict()
        alleleInd={'A':4,'C':5,'G':6,'T':7}
        # Convert to Dict
        for f in config:
            if len(f)==4:
                fpIndices[f[0]+':'+f[1]]=[alleleInd[f[2]],alleleInd[f[3]],f[0]+':'+f[1]]
            elif len(f)==5:
                fpIndices[f[0]+':'+f[1]]=[alleleInd[f[2]],alleleInd[f[3]],f[4]]
        n=len(fpIndices.keys())
        return fpIndices, n

###################
#Make Output Dir Functions
###################
def MakeOutputDir (OutputDir):
    if os.path.exists(OutputDir):
        if os.path.exists(OutputDir+'/FPResults'):
            raise IOError('Error FPResults already exist in the OutputDir, either remove or rename Older directory')
        else:
            os.mkdir(OutputDir+'/FPResults')
            return OutputDir+'/FPResults/'
    else:
        raise IOError('Error: Output directory does not exist')

###################
##Run Analysis
###################
def extractRawFP (pileupfile, fpIndices):
    pileup=readCVS(pileupfile)
    fpRaw=[]
    for p in pileup:
        if p[0]+':'+p[1] in fpIndices.keys() and p[0]+':'+p[1] not in [f[0]+':'+f[1] for f in fpRaw]:
            fpRaw.append(p[0:8])
    name=os.path.basename(pileupfile)
    fpRaw.insert(0,[name])
    return fpRaw


def FindFPMAF (listofpileups, fpIndices, fpOutputdir):
    All_FP=[]
    All_geno=[]
    Alleles=['A','C','G','T']
    thres=0.1
    for pileupfile in listofpileups:
        fpRaw=extractRawFP(pileupfile, fpIndices)
        #writeCVS (fpOutputdir+'FP_counts.txt', fpRaw)
        name=fpRaw.pop(0)
        if All_FP==[]:
            header=[fpIndices[eachfp[0]+':'+eachfp[1]][2] for eachfp in fpRaw]
            header.insert(0,'Sample')
            All_FP.append(header)
            All_geno.append(header)
        FPmAF=[min(counts)/sum(counts) if sum(counts)!=0 else 999 for counts in [[int(eachfp[index]) for index in fpIndices[eachfp[0]+':'+eachfp[1]][0:2]] for eachfp in fpRaw]]
        FPGeno=[Alleles[np.argmax([int(F) for F in f[4::]])] if FPmAF[i]<=thres else "Het" for i,f in enumerate(fpRaw)]
        FPmAF.insert(0,name[0])
        FPGeno.insert(0,name[0])
        All_FP.append(FPmAF)
        All_geno.append(FPGeno)
        for p in fpRaw:
            p.insert(0,name[0])
        writeCVS (fpOutputdir+'FP_counts.txt', fpRaw)
    writeCVS(fpOutputdir+'FP_mAF.txt', All_FP)
    writeCVS(fpOutputdir+'FP_Geno.txt', All_geno)
    return All_FP, All_geno

def ContaminationRate (All_FP):
    contamination =[]
    All_FP=All_FP[1::]
    for sample in All_FP:
      homozygous = [x for x in sample[1::] if x<=.1]
      if len(homozygous)!=0:
        contamination.append([sample[0], np.mean(homozygous)])
      else:
        contamination.append([sample[0], 'NaN'])
    return contamination


def compare_genotype (All_geno, n, fpOutputdir, expectedFile='none'):
    if os.path.isfile(expectedFile):
        expected =readCVS(expectedFile)
    else:
        print('Expected List not found')
        expected =[]

    if All_geno[0][0]=='Sample':
        All_geno=All_geno[1::]

    All_geno=[a for a in All_geno if 'CELLFREEPOOLEDNORMAL' not in a[0]]
    Geno_Compare=[]
    for i,g in enumerate(All_geno):
        for h in All_geno[i+1::]:
            hmMatch=0
            hmMisMatch=0
            htMatch=0
            htMisMatch=0
            TotalMatch=0
            for j, element in enumerate(g):
                if element==h[j]:
                    TotalMatch=TotalMatch+1
                    if element=='Het':
                        htMatch=htMatch+1
                    else:
                        hmMatch=hmMatch+1
                elif element=='Het' or h[j]=='Het':
                    htMisMatch=htMisMatch+1
                elif j!=0:
                    hmMisMatch=hmMisMatch+1
            Geno_Compare.append([g[0][0:g[0].find('_bc')],h[0][0:h[0].find('_bc')], TotalMatch, hmMatch, hmMisMatch, htMatch, htMisMatch])
    sort_index = np.argsort([x[2] for x in Geno_Compare])
    Geno_Compare=[Geno_Compare[i] for i in sort_index]

    mlist=[i for i, x in enumerate([g[2] for g in Geno_Compare]) if x/n>.8]
    if mlist!=[]:
        m=min(mlist)
    else:
        m=len(Geno_Compare)
    expectedInd=[]
    for y in expected:
        for i,x in enumerate(Geno_Compare):
            if [x[0],x[1]]==y or [x[1],x[0]]==y:
                expectedInd.append(i)
    for i, x in enumerate(Geno_Compare):
        if i<m:
            if i in expectedInd:
                x.append('Unexpected Mismatch')
            else:
                x.append('Expected Mismatch')
        else:
           if i in expectedInd:
               x.append('Expected Match')
           else:
               x.append('Unexpected Match')
    Geno_Compare.insert(0,["Sample1","Sample2", "TotalMatch", "HomozygousMatch", "HomozygousMismatch", "HeteozygousMatch", "HeteozygousMismatch", "Status"])
    writeCVS(fpOutputdir+'Geno_compare.txt', Geno_Compare)
    return Geno_Compare

###################
##Plot Functions
###################

def plotMinorContamination(All_FP, fpOutputdir):
    plt.clf()
    contamination=ContaminationRate (All_FP)
    contamination=[x for x in contamination if x[1]!='NaN']
    samplename =[c[0][0:c[0].find('_bc')] for c in contamination]
    y_pos = np.arange(len(samplename))
    meanContam = [c[1] for c in contamination]
    minorContamination=[[samplename[i],meanContam[i]] for i in range(0,len(samplename))]
    minorContamination=sorted(minorContamination)
    writeCVS(fpOutputdir+'minorContamination.txt', minorContamination)

    plt.figure(figsize=(10, 5))
    plt.axhline(y=0.02, xmin=0, xmax=1, c='r', ls='--')
    plt.axhline(y=0.01, xmin=0, xmax=1, c='orange', ls='--')
    plt.bar(y_pos, [m[1] for m in minorContamination], align='edge', color='black')
    plt.xticks(y_pos, [m[0] for m in minorContamination], rotation=90, ha='left')
    plt.ylabel('Avg. Minor Allele Frequency at Homozygous Position')
    plt.xlabel('Sample Name')
    plt.title('Minor Contamination Check')
    plt.xlim([0,y_pos.size])
    plt.savefig(fpOutputdir+'/MinorContaminationRate.pdf', bbox_inches='tight')

def plotMajorContamination(All_geno, fpOutputdir):
    plt.clf()
    if All_geno[0][0]=='Sample':
        All_geno=All_geno[1::]
    samples=[g[0].split('_bc')[0] for g in All_geno]
    x_pos=np.arange(len(All_geno))
    pHet=[sum([1 for a in g if a=='Het'])/(len(g)-1) for g in All_geno]

    majorContamination=[[samples[i],pHet[i]] for i in range(0,len(samples))]
    majorContamination=sorted(majorContamination)
    writeCVS(fpOutputdir+'majorContamination.txt', majorContamination)

    plt.axhline(y=0.55, xmin=0, xmax=1, c='r', ls='--')
    plt.bar(x_pos, [m[1] for m in majorContamination], align='edge', color='black')
    plt.xticks(x_pos, [m[0] for m in majorContamination], rotation=90, ha='left')
    plt.ylabel('% of Heterozygous Position')
    plt.xlabel('Sample Name')
    plt.title('Major Contamination Check')
    plt.xlim([0,x_pos.size])
    plt.savefig(fpOutputdir+'MajorContaminationRate.pdf', bbox_inches='tight')

def plotGenoCompare (Geno_Compare,n, fpOutputdir):
    plt.clf()
    if Geno_Compare[0][0]=="Sample1":
        Geno_Compare=Geno_Compare[1::]
    Geno_Compare=[x for x in Geno_Compare if x[7]!='Expected Mismatch']
    if Geno_Compare:
        samples=[c[0]+' : '+c[1] for c in Geno_Compare]
        y_pos = np.arange(len(Geno_Compare))
        plt.figure(figsize=(5, 5))
        for i, g in enumerate(Geno_Compare):
            if g[7]=='Unexpected Match':
                plt.axhspan(i, i+1, facecolor='.5', alpha=0.5)
        plt.axvline(x=0, ymin=0, ymax=1, c='black', ls='-', linewidth=2)
        plt.axvline(x=0.8, ymin=0, ymax=1, c='black', ls='--')
        newmlist=[i for i, x in enumerate([g[2] for g in Geno_Compare]) if x/n>.8]
        if newmlist:
            newm=min(newmlist)
            plt.axhline(y=newm-.15, xmin=0, xmax=1, c='red', ls=':', linewidth=3)
        plt.barh(y_pos, [(g[3]+g[5])/n for g in Geno_Compare], align='edge', color='#ff9b9b', alpha=0.5, label='Matched Homozygous')
        plt.barh(y_pos, [g[5]/n for g in Geno_Compare], align='edge', color='#b9d6c8', label='Matched Heterozygous')
        plt.barh(y_pos, [(-g[4]-g[6])/n for g in Geno_Compare], align='edge', color='#d1909c', label='Mismatched Homozygous')
        plt.barh(y_pos, [-g[6]/n for g in Geno_Compare], align='edge', color='#7f9990', label='Mismatched Heterozygous')
        plt.yticks(y_pos, samples, va='bottom')
        plt.axes().yaxis.grid()

        plt.legend(bbox_to_anchor=(1.8, 0.5))
        plt.xlabel('Fingerprint Comparision')
        plt.ylabel('Samples Compared')
        plt.title('Fraction of Matching Fingerprints', fontsize=16)
        plt.savefig(fpOutputdir+'Selectfpcompare.pdf',bbox_inches='tight')

######################
#Convert Txt files

def convertFP_mAF(InputDir, OutputDir):
    x=readCVS(InputDir+'FP_mAF.txt')
    All_FP=[]
    for sample in x[1::]:
        new=[float(i) for i in sample[1::]]
        new.insert(0, sample[0])
        All_FP.append(new)
    All_FP.insert(0, x[0])
    return All_FP

######################
#Main Function
######################

def runFPreport (OutputDir, WaltzDir= '.', configFile='/home/hasanm/Innovation/sandbox/Maysun/FingerPrinting/testPipeline/justFPSnps.txt' , expectedFile='none'):
    #try:
    listofpileups=Extractpileupfiles (WaltzDir)
    fpIndices, n=createFPIndices(configFile)
    fpOutputdir=MakeOutputDir (OutputDir)
    All_FP, All_geno=FindFPMAF (listofpileups, fpIndices, fpOutputdir)
    Geno_Compare=compare_genotype (All_geno, n, fpOutputdir, expectedFile)

    #plots
    plotMinorContamination(All_FP, fpOutputdir)
    plotMajorContamination(All_geno, fpOutputdir)
    plotGenoCompare (Geno_Compare,n, fpOutputdir)
    mergePdfInFolder(fpOutputdir, fpOutputdir, 'FPFigures.pdf')
    #return listofpileups, fpIndices, n, All_FP, All_geno, Geno_Compare
    # except IOError as err:
    #     print(err.args)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_dir", help="Directory to write the Output files to", required=True)
    parser.add_argument("-w", "--waltz_dir", help="Directory with waltz pileup files", required=True)
    parser.add_argument("-c", "--fp_config", help="File with information about the SNPs for analysis", required=True)
    parser.add_argument("-e", "--expected_match", help="File with the expected samples matches", required=False)
    args = parser.parse_args()
    return args

def main ():
    args= parse_arguments()
    if args.expected_match: #if it exsists
        runFPreport(OutputDir=args.output_dir, WaltzDir=args.waltz_dir, configFile=args.fp_config, expectedFile=args.expected_match)
    else:
       runFPreport(OutputDir=args.output_dir, WaltzDir=args.waltz_dir, configFile=args.fp_config)

#    runFPreport(OutputDir='/home/hasanm/Innovation/sandbox/Maysun/FingerPrinting/testPipeline/', WaltzDir='/home/hasanm/Innovation/sandbox/Maysun/FingerPrinting/testPipeline/waltz/', configFile='/home/hasanm/Innovation/sandbox/Maysun/FingerPrinting/testPipeline/testFPconfig.txt')

if __name__ == '__main__':
    main()