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

from python_tools.util import read_df, extract_sample_name, autolabel
from python_tools.constants import *


def noise_alt_percent_plot(noise_table):
    samples = noise_table[SAMPLE_ID_COLUMN].tolist()
    alt_percent = noise_table['AltPercent']
    y_pos = np.arange(len(samples))

    plt.clf()
    plt.figure(figsize=(10, 5))
    bars = plt.bar(y_pos, alt_percent, align='center', color='black')
    plt.axhline(y=0.001, xmin=0, xmax=1, c='y', ls='--')
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
    plt.axhline(y=1000, xmin=0, xmax=1, c='y', ls='--')
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

        The input table will be converted from 12 noise classes, to 6
        (see `substitution_classes` groupings).
    :return:
    """
    substitution_classes = [
        [['G>T', 'C>A'], 'C>A'],
        [['C>G', 'G>C'], 'C>G'],
        [['G>A', 'C>T'], 'C>T'],
        [['T>A', 'A>T'], 'T>A'],
        [['A>G', 'T>C'], 'T>C'],
        [['T>G', 'A>C'], 'T>G'],
    ]
    all_samples = noise_by_substitution_table[SAMPLE_ID_COLUMN].unique()

    # Loop through samples and combine substitutions into 6 classes
    six_class_noise_by_substitution = pd.DataFrame(columns=['Sample', 'Class', 'AltPercent'])
    for sample in all_samples:
        for class_pair in substitution_classes:
            original_classes = class_pair[0]
            final_label = class_pair[1]

            substitution_class_boolv = noise_by_substitution_table['Substitution'].isin(original_classes)
            sample_boolv = noise_by_substitution_table[SAMPLE_ID_COLUMN] == sample
            subset = noise_by_substitution_table[substitution_class_boolv & sample_boolv]
            combined_class_altcount = float(subset['AltCount'].sum())
            combined_class_genotype_count = float(subset['GenotypeCount'].sum())
            class_noise = combined_class_altcount / (combined_class_altcount + combined_class_genotype_count + EPSILON)

            # Change from fraction to percent
            class_noise = class_noise * 100.0
            new = pd.DataFrame({
                'Sample': [sample],
                'Class': final_label,
                'AltPercent': class_noise
            })
            six_class_noise_by_substitution = six_class_noise_by_substitution.append(new)

    sns.set_style('darkgrid', {'axes.facecolor': '.9'})
    plt.clf()
    plt.figure(figsize=(10, 5))

    # Variable to help only putting y-axis title on subplots in first column
    num_cols = 6
    g = sns.FacetGrid(six_class_noise_by_substitution, col='Sample', col_wrap=num_cols, sharey=True)
    g = g.map(plt.bar, 'Class', 'AltPercent')

    g.set_titles(row_template='Noise (%)', col_template='{col_name}')
    for i, ax in enumerate(g.axes.flat):
        if i % num_cols == 0:
            ax.set_ylabel('Noise (%)')
        ax.set_xlabel('')
        plt.setp(ax.get_xticklabels(), visible=True)
        plt.setp(ax.get_xticklabels(), rotation=45)

    g.fig.subplots_adjust(top=0.8, wspace=0.1, hspace=0.35)
    g.fig.suptitle('Noise by Substitution Class')

    # Save table and figure
    six_class_noise_by_substitution.to_csv('noise_by_substitution.tsv', sep='\t', index=False)
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

    # Filter to just Plasma samples (if there are any)
    plasma_samples = noise_and_title_file[noise_and_title_file[MANIFEST__SAMPLE_TYPE_COLUMN] == 'Plasma'][SAMPLE_ID_COLUMN]
    plasma_noise_by_substitution = noise_by_substitution_table[noise_by_substitution_table[MANIFEST__SAMPLE_TYPE_COLUMN] == 'Plasma'][SAMPLE_ID_COLUMN]
    if not len(plasma_samples) == 0:
        noise_boolv = noise_and_title_file[SAMPLE_ID_COLUMN].isin(plasma_samples)
        noise_and_title_file = noise_and_title_file.loc[noise_boolv]
        noise_by_substitution_boolv = noise_by_substitution_table[SAMPLE_ID_COLUMN].isin(plasma_noise_by_substitution)
        noise_by_substitution_table = noise_by_substitution_table.loc[noise_by_substitution_boolv]

    # Sort in same order as R code (by sample class)
    # Use a stable mergesort instead of quicksort default
    noise_and_title_file = noise_and_title_file.sort_values(MANIFEST__SAMPLE_CLASS_COLUMN, kind='mergesort').reset_index(drop=True)
    noise_by_substitution_table = noise_by_substitution_table.sort_values(MANIFEST__SAMPLE_CLASS_COLUMN, kind='mergesort').reset_index(drop=True)

    noise_alt_percent_plot(noise_and_title_file)
    noise_contributing_sites_plot(noise_and_title_file)
    noise_by_substitution_plot(noise_by_substitution_table)
