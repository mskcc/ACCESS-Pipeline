#!python
# -*- coding: utf-8 -*-

import argparse
import matplotlib
# For Local:
# matplotlib.use('TkAgg')
# For Luna:
matplotlib.use('Agg')

import seaborn as sns
import matplotlib.pyplot as plt

from python_tools.constants import *
from python_tools.util import merge_files_across_samples


def read_quality_tables(picard_metrics_directory_path):
    """
    Read tables from picard outputs folder

    :param picard_metrics_directory_path: Picard metrics directory with .quality_by_cycle_metrics files
    :return:
    """
    picard_metrics = os.listdir(picard_metrics_directory_path)
    metrics_files = [f for f in picard_metrics if '.quality_by_cycle_metrics' in f]
    # Add folder name prefix
    metrics_files = [os.path.join(picard_metrics_directory_path, f) for f in metrics_files]

    qual_metrics_df = merge_files_across_samples(
        metrics_files,
        ['CYCLE', 'MEAN_QUALITY', 'MEAN_ORIGINAL_QUALITY'],
        skiprows=7,
        header=0
    )
    return qual_metrics_df


def base_quality_plot(quality_table):
    """
    Create the base quality plots with original and new quality scores by cycle, and save to pdf

    :param quality_table: Picard base quality table aggregated across samples
    :return:
    """
    sns.set()
    fig, axes = plt.subplots(2, 1, figsize=(15.0, 7.5))
    axes[0].set_title('Recalibration Qualtiy Scores')

    ax = sns.lineplot(
        data = quality_table,
        x = 'CYCLE',
        y = 'MEAN_ORIGINAL_QUALITY',
        hue = SAMPLE_ID_COLUMN,
        ax = axes[0],
        linewidth=1.2
    )
    ax.get_legend().remove()
    ax.set_ylabel('Base Quality Score')
    ax.set_xlabel('Cycle')
    # Static y-limits for
    ax.set_ylim([0, 50])

    # Move figures away from legend
    LEFT_SHIFT = 0.05
    box = ax.get_position()
    ax.set_position([box.x0 - LEFT_SHIFT, box.y0, box.width - LEFT_SHIFT, box.height])

    ax = sns.lineplot(
        data = quality_table,
        x = 'CYCLE',
        y = 'MEAN_QUALITY',
        hue = SAMPLE_ID_COLUMN,
        ax = axes[1],
        linewidth=1.2
    )
    ax.get_legend().remove()
    ax.set_xlabel('')
    ax.set_ylabel('Recalibrated Base Quality Score')

    box = ax.get_position()
    ax.set_position([box.x0 - LEFT_SHIFT, box.y0, box.width - LEFT_SHIFT, box.height])

    plt.xlabel('Cycle')
    # Single legend for both plots
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles=handles[1:], labels=labels[1:], loc='center right')

    plt.savefig('base_quality_plot.pdf', bbox_inches='tight')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--picard_metrics_directory', required=True)
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    quality_table = read_quality_tables(args.picard_metrics_directory).fillna(0)
    base_quality_plot(quality_table)
