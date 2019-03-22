#!python
# -*- coding: utf-8 -*-

import logging
import argparse
import matplotlib
# For Local:
# matplotlib.use('TkAgg')
# For Luna:
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt

from ...util import read_df, extract_sample_name, autolabel
from ...constants import *


def noise_alt_percent_plot(noise_table):
    samples = noise_table[TITLE_FILE__SAMPLE_ID_COLUMN].tolist()
    alt_percent = noise_table['AltPercent']
    y_pos = np.arange(len(samples))

    plt.clf()
    plt.figure(figsize=(10, 5))
    bars = plt.bar(y_pos, alt_percent, align='center', color='black')
    plt.axhline(y=0.001, xmin=0, xmax=1, c='r', ls='--')
    plt.axhline(y=0.0004, xmin=0, xmax=1, c='y', ls='--')
    plt.xticks(y_pos, samples, rotation=90, ha='center')

    # Put the values on top of the bars
    autolabel(bars, plt)

    plt.xlim([-1, len(samples)])
    plt.ylabel('Noise (%)')
    plt.xlabel('Sample Name')
    plt.title('Noise Level')
    plt.savefig('NoiseAltPercent.pdf', bbox_inches='tight')


def noise_contributing_sites_plot(noise_table):
    samples = noise_table[TITLE_FILE__SAMPLE_ID_COLUMN].tolist()
    contributing_sites = noise_table['ContributingSites']
    y_pos = np.arange(len(samples))

    plt.clf()
    plt.figure(figsize=(10, 5))
    bars = plt.bar(y_pos, contributing_sites, align='center', color='black')
    plt.axhline(y=400, xmin=0, xmax=1, c='y', ls='--')
    plt.xticks(y_pos, samples, rotation=90, ha='center')

    # Put the values on top of the bars
    autolabel(bars, plt, text_format='%d')

    plt.xlim([-1, len(samples)])
    plt.ylabel('Number of Contributing Sites')
    plt.xlabel('Sample Name')
    plt.title('Contributing Sites for Noise')
    plt.savefig('NoiseContributingSites.pdf', bbox_inches='tight')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--noise_file", required=True)
    parser.add_argument("-ns", "--noise_by_substitution", required=False)
    parser.add_argument("-t", "--title_file", required=True)
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    noise_table = read_df(args.noise_file, header='infer').fillna(0)
    title_file = read_df(args.title_file, header='infer')

    print('Plotting Noise:')
    print(noise_table)
    print(title_file)

    # Filter to just Total reads noise counts
    noise_table = noise_table[noise_table['Method'] == 'Total']

    # Cleanup sample IDs (in Noise table as well as Title File)
    sample_ids = title_file[TITLE_FILE__SAMPLE_ID_COLUMN].tolist()
    noise_table[TITLE_FILE__SAMPLE_ID_COLUMN] = noise_table[TITLE_FILE__SAMPLE_ID_COLUMN].apply(extract_sample_name, args=(sample_ids,))

    # Merge noise with title file
    noise_and_title_file = noise_table.merge(title_file, on = TITLE_FILE__SAMPLE_ID_COLUMN)

    # Filter to Plasma samples
    plasma_samples = noise_and_title_file[noise_and_title_file[TITLE_FILE__SAMPLE_TYPE_COLUMN] == 'Plasma'][TITLE_FILE__SAMPLE_ID_COLUMN]
    boolv = noise_and_title_file[TITLE_FILE__SAMPLE_ID_COLUMN].isin(plasma_samples)
    noise_and_title_file = noise_and_title_file.loc[boolv]

    # Sort in same order as R code (by sample class)
    noise_and_title_file = noise_and_title_file.sort_values(TITLE_FILE__CLASS_COLUMN).reset_index(drop=True)

    print('Noise Table:')
    print(noise_and_title_file)

    noise_alt_percent_plot(noise_and_title_file)
    noise_contributing_sites_plot(noise_and_title_file)
