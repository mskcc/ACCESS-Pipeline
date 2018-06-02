#!python
# -*- coding: utf-8 -*-


import csv
import argparse
import matplotlib
matplotlib.use('TkAgg')

import numpy as np
import matplotlib.pyplot as plt



def readCVS(filename):
  data = []
  with open(filename, 'r') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
      data.append(row)
  return data
  

def NoiseAltPercentPlot(noise_file):
    plt.clf()
    noise=readCVS(noise_file)
    print(noise)
    noise.pop(0)
    altPercent = [[n[0][0:n[0].find('IGO')], float(n[3])] for n in noise if n[5]=='Total']
    y_pos = np.arange(len(altPercent))
    altPercent = sorted(altPercent)
    plt.figure(figsize=(10, 5))
    plt.bar(y_pos, [m[1] for m in altPercent], align='edge', color='black')
    plt.xticks(y_pos, [m[0] for m in altPercent], rotation=90, ha='left')
    plt.ylabel('Noise (%)')
    plt.xlabel('Sample Name')
    plt.title('Noise Level')
    plt.xlim([0,y_pos.size])
    plt.savefig('./NoiseAltPercent.pdf', bbox_inches='tight')


def NoiseContributingSitesPlot(noise_file):
    plt.clf()
    noise=readCVS(noise_file)
    noise.pop(0)
    print noise
    altPercent = [[n[0][0:n[0].find('IGO')], int(n[4])] for n in noise if n[5]=='Total']
    y_pos = np.arange(len(altPercent))
    altPercent = sorted(altPercent)
    plt.figure(figsize=(10, 5))
    plt.bar(y_pos, [m[1] for m in altPercent], align='edge', color='black')
    plt.xticks(y_pos, [m[0] for m in altPercent], rotation=90, ha='left')
    plt.ylabel('Number of Contributing Sites')
    plt.xlabel('Sample Name')
    plt.title('Contributing Sites for Noise')
    plt.xlim([0,y_pos.size])
    plt.savefig('./NoiseContributingSites.pdf', bbox_inches='tight')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--noise_file", help="Directory to write the Output files to", required=True)
    parser.add_argument("-ns", "--noise_by_substitution", help="Directory with waltz pileup files", required=True)
    args = parser.parse_args()
    return args


def main ():
    args= parse_arguments()
    NoiseAltPercentPlot(args.noise_file)
    NoiseContributingSitesPlot(args.noise_file)
    
    
if __name__ == '__main__':
    main()
