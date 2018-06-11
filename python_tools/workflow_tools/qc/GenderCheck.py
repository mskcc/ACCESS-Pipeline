#!python
# -*- coding: utf-8 -*-
"""
Created on Wed May 30 12:17:18 2018

@author: hasanm
"""

import csv
import os
import pandas as pd
import argparse

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt



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



def FindSexFromPileup (WaltzDir, OutputDir):
  #Not Currently Used: Checks the pileups if there are more that 200 positions in the Y chromosome with at least 1 read, the sample is classified as male.
    sex=[]
    for file in os.listdir(WaltzDir):
        if file[-10::]=='pileup.txt':
            data = []
            with open(WaltzDir+'/'+file, 'r') as f:
              reader = csv.reader(f, delimiter='\t')
              for row in reader:
                if row[0]=='Y':
                    if int(row[3])>0:
                        data.append(row[3])
    
            if len(data)>200:
                sex.append([file[0:file.find('_bc')],"Male"])
            else:
                sex.append([file[0:file.find('_bc')],"Female"])
    writeCVS(OutputDir+'/Sample_sex_from_pileup.txt', sex)
    return sex

def FindSexFromInterval (WaltzDir, OutputDir):
  #Used: Checks the Interval files if the sum of the average coverage per interval (2 on Y) is greater that 50, the sample is classified as male.
    sex=[]
    for file in os.listdir(WaltzDir):
        if file[-13::]=='intervals.txt':
            data = []
            with open(WaltzDir+'/'+file, 'r') as f:
              reader = csv.reader(f, delimiter='\t')
              for row in reader:
                if row[3]=='Tiling_SRY_Y:2655301' or row[3]=='Tiling_USP9Y_Y:14891501':
                    data.append(row[5])
    
            if sum(data)>50:
                sex.append([file[0:file.find('_bc')],"Male"])
            else:
                sex.append([file[0:file.find('_bc')],"Female"])
    writeCVS(OutputDir+'/Sample_sex_from_pileup.txt', sex)
    return sex
        
def standardizeGender(titleFile):
    ##Potential inputs    
    female=['female','f','Female', 'F']
    male=['Male','M','male', 'm']
    ##
    titleInfo=readCVS(titleFile)
    gender_from_title=[[t[2],t[11]] for t in titleInfo]
    gender=[]
    for s in gender_from_title:
        if s[1] in female:
            gender.append([s[0].replace('_', '-'),'Female'])
        elif s[1] in male:
            gender.append([s[0].replace('_', '-'),'Male'])
    return gender
            
    
def CheckSex (gender, sex, OutputDir):
    list_of_samples=[s[0] for s in sex]  
    MisMatchSex=[]
    for g in gender:
        if g[0] in list_of_samples:
            idx=list_of_samples.index(g[0])
            if g[1]!=sex[idx][1]:
                MisMatchSex.append([g[0], g[1], sex[idx][1]])
    if MisMatchSex:
        df = pd.DataFrame(MisMatchSex, columns=["Sample","GenderFromTitleFile", "SexFromPileup"])
        writeCVS(OutputDir+'/MisMatchedGender.txt', MisMatchSex)
        plt.clf()
        fig, ax = plt.subplots()
        plt.title('Gender MisMatch')
        ax.axis('off')
        ax.axis('tight')
        ax.table(cellText=df.values, colLabels=df.columns, loc='center')
        fig.tight_layout()
        plt.savefig(OutputDir+'/GenderMisMatch.pdf',bbox_inches='tight')
        

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_dir", help="Directory to write the Output files to", required=True)
    parser.add_argument("-w", "--waltz_dir", help="Directory with waltz pileup files", required=True)
    parser.add_argument("-t", "--title_file", help="Title File for Run", required=True)
    args = parser.parse_args()
    return args

def main ():
    args= parse_arguments()
    sex=FindSexFromInterval(WaltzDir=args.waltz_dir, OutputDir=args.output_dir)
    gender=standardizeGender(titleFile=args.title_file)
    CheckSex(gender, sex, OutputDir=args.output_dir)
    
if __name__ == '__main__':
    main()


