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
import seaborn as sns
import matplotlib.pyplot as plt

from ...util import read_df, extract_sample_name, autolabel
from ...constants import *


def noise_alt_percent_plot(noise_table):
    samples = noise_table[SAMPLE_ID_COLUMN].tolist()
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
    samples = noise_table[SAMPLE_ID_COLUMN].tolist()
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


def noise_by_substitution_plot(noise_by_substitution_table):
    """
    :param noise_by_substitution_table: pd.DataFrame with columns:
        CMO_SAMPLE_ID: string
        Substitution: string
        GenotypeCount: int
        AltCount: int
        AltPercent: float
        ContributingSites: int
        Method: string
    :return:
    """
    substitution_classes = [
        [['T>A', 'A>T'], 'T/A>A/T'],
        [['A>G', 'T>C'], 'A/T>G/C'],
        [['G>A', 'C>T'], 'G/C>A/T'],
        [['C>G', 'G>C'], 'C/G>G/C'],
        [['T>G', 'A>C'], 'T/A>G/C'],
        [['G>T', 'C>A'], 'G/C>T/A']
    ]
    all_samples = noise_by_substitution_table[SAMPLE_ID_COLUMN].unique()

    six_class_noise_by_substitution = pd.DataFrame(columns=['Sample', 'Class', 'AltPercent'])
    # Todo: Iteratively appending rows to a DataFrame can be more computationally intensive than a single concatenate.
    # A better solution is to append those rows to a list and then concatenate the list with the original DataFrame all at once.
    for sample in all_samples:
        for class_pair in substitution_classes:
            original_classes = class_pair[0]
            final_label = class_pair[1]

            substitution_class_boolv = noise_by_substitution_table['Substitution'].isin(original_classes)
            sample_boolv = noise_by_substitution_table[SAMPLE_ID_COLUMN] == sample
            subset = noise_by_substitution_table[substitution_class_boolv & sample_boolv]

            # Todo: should be (alt / (alt + geno)) or (alt / geno)?
            combined_class_altcount = float(subset['AltCount'].sum())
            combined_class_genotype_count = float(subset['GenotypeCount'].sum())
            class_noise = combined_class_altcount / (combined_class_altcount + combined_class_genotype_count)

            # Change from fraction to percent
            class_noise = class_noise * 100.0
            new = pd.DataFrame({'Sample': [sample], 'Class': final_label, 'AltPercent': class_noise})
            six_class_noise_by_substitution = six_class_noise_by_substitution.append(new)

    sns.set_style("darkgrid", {"axes.facecolor": ".9", 'ytick.left': True, 'ytick.right': False})
    plt.clf()
    plt.figure(figsize=(10, 5))
    g = sns.FacetGrid(six_class_noise_by_substitution, col='Class', col_wrap=3, sharey=True)
    g = g.map(plt.bar, 'Sample', 'AltPercent')

    for ax in g.axes.flat:
        ax.yaxis.set_label_position('left')
        plt.setp(ax.xaxis.get_majorticklabels(), ha='left')
        ax.yaxis.tick_left()

    g.set_xticklabels(rotation=90)
    g.fig.subplots_adjust(wspace=.1, hspace=.15)
    plt.savefig('noise_by_substitution.pdf', bbox_inches='tight')
    return six_class_noise_by_substitution


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--title_file", required=True)
    parser.add_argument("-n", "--noise_file", required=True)
    parser.add_argument("-ns", "--noise_by_substitution", required=True)
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    noise_table = read_df(args.noise_file, header='infer').fillna(0)
    noise_by_substitution_table = read_df(args.noise_by_substitution, header='infer').fillna(0)
    title_file = read_df(args.title_file, header='infer')

    print('Plotting Noise:')
    print(noise_table)
    print(title_file)
    print(noise_by_substitution_table)

    # Filter to just Total reads noise counts
    noise_table = noise_table[noise_table['Method'] == 'Total']
    noise_by_substitution_table = noise_by_substitution_table[noise_by_substitution_table['Method'] == 'Total']

    # Cleanup sample IDs (in Noise table as well as Title File)
    sample_ids = title_file[SAMPLE_ID_COLUMN].tolist()
    noise_table[SAMPLE_ID_COLUMN] = noise_table[SAMPLE_ID_COLUMN].apply(extract_sample_name, args=(sample_ids,))
    noise_by_substitution_table[SAMPLE_ID_COLUMN] = noise_by_substitution_table[SAMPLE_ID_COLUMN].apply(extract_sample_name, args=(sample_ids,))

    # Merge noise with title file
    noise_and_title_file = noise_table.merge(title_file, on = SAMPLE_ID_COLUMN)
    noise_by_substitution_table = noise_by_substitution_table.merge(title_file, on = SAMPLE_ID_COLUMN)

    # Filter to Plasma samples
    plasma_samples = noise_and_title_file[noise_and_title_file[MANIFEST__SAMPLE_TYPE_COLUMN] == 'Plasma'][SAMPLE_ID_COLUMN]
    plasma_noise_by_substitution = noise_by_substitution_table[noise_by_substitution_table[MANIFEST__SAMPLE_TYPE_COLUMN] == 'Plasma'][SAMPLE_ID_COLUMN]

    boolv = noise_and_title_file[SAMPLE_ID_COLUMN].isin(plasma_samples)
    noise_by_substitution_boolv = noise_by_substitution_table[SAMPLE_ID_COLUMN].isin(plasma_noise_by_substitution)
    noise_and_title_file = noise_and_title_file.loc[boolv]
    noise_by_substitution_table = noise_by_substitution_table.loc[noise_by_substitution_boolv]

    # Sort in same order as R code (by sample class)
    noise_and_title_file = noise_and_title_file.sort_values(MANIFEST__SAMPLE_CLASS_COLUMN).reset_index(drop=True)
    noise_by_substitution_table = noise_by_substitution_table.sort_values(MANIFEST__SAMPLE_CLASS_COLUMN).reset_index(drop=True)

    noise_alt_percent_plot(noise_and_title_file)
    noise_contributing_sites_plot(noise_and_title_file)
    noise_by_substitution_plot(noise_by_substitution_table)
