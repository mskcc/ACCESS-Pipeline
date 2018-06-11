#!python
# -*- coding: utf-8 -*-

import argparse
import matplotlib
# For Local:
# matplotlib.use('TkAgg')
# For Luna:
matplotlib.use('Agg')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ...util import read_df


def NoiseAltPercentPlot(noise_table):
    samples = noise_table['Sample'].str.replace('[_-]IGO.*', '').unique()
    alt_percent = noise_table[noise_table['Method'] == 'Total']['AltPercent']
    y_pos = np.arange(len(samples))

    plt.clf()
    plt.figure(figsize=(10, 5))
    plt.bar(y_pos, alt_percent, align='center', color='black')
    plt.xticks(y_pos, samples, rotation=90, ha='center')
    plt.xlim([-1, len(samples)])
    plt.ylabel('Noise (%)')
    plt.xlabel('Sample Name')
    plt.title('Noise Level')
    plt.savefig('./NoiseAltPercent.pdf', bbox_inches='tight')


def NoiseContributingSitesPlot(noise_table):
    samples = noise_table['Sample'].str.replace('[_-]IGO.*', '').unique()
    contributing_sites = noise_table[noise_table['Method'] == 'Total']['ContributingSites']
    y_pos = np.arange(len(samples))

    plt.clf()
    plt.figure(figsize=(10, 5))
    plt.bar(y_pos, contributing_sites, align='center', color='black')
    plt.xticks(y_pos, samples, rotation=90, ha='center')
    plt.xlim([-1, len(samples)])
    plt.ylabel('Number of Contributing Sites')
    plt.xlabel('Sample Name')
    plt.title('Contributing Sites for Noise')
    plt.savefig('./NoiseContributingSites.pdf', bbox_inches='tight')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--noise_file", help="Directory to write the Output files to", required=True)
    parser.add_argument("-ns", "--noise_by_substitution", help="Directory with waltz pileup files", required=True)
    args = parser.parse_args()
    return args


def main ():
    args= parse_arguments()
    noise_table = pd.read_csv(args.noise_file, sep='\t').fillna(0)
    NoiseAltPercentPlot(noise_table)
    NoiseContributingSitesPlot(noise_table)
    
    
if __name__ == '__main__':
    main()
