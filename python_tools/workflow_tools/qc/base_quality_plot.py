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
    print("PICARD DIR: {}".format(picard_metrics))
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
    Create the base quality plots with original and new quality scores by cycle

    :param quality_table: Picard base quality table aggregated across samples
    :return:
    """
    f, axes = plt.subplots(2, 1)

    ax = sns.lineplot(
        x = 'CYCLE',
        y = 'MEAN_QUALITY',
        hue = SAMPLE_ID_COLUMN,
        # style = "choice",
        data = quality_table,
        ax = axes[0]
    )

    box = ax.get_position()
    # resize position
    ax.set_position([box.x0, box.y0, box.width * 0.70, box.height])
    # Put legend to the right side
    ax.legend(loc='center right', bbox_to_anchor=(1.55, 0.5), ncol=1)

    ax = sns.lineplot(
        x = 'CYCLE',
        y = 'MEAN_ORIGINAL_QUALITY',
        hue = SAMPLE_ID_COLUMN,
        # style = "choice",
        data = quality_table,
        ax = axes[1]
    )

    box = ax.get_position()
    # resize position
    ax.set_position([box.x0, box.y0, box.width * 0.70, box.height])
    # Put legend to the right side
    ax.legend(loc='center right', bbox_to_anchor=(1.55, 0.5), ncol=1)

    plt.savefig('base_quality_plot.pdf')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--picard_metrics_directory', required=True)
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()
    quality_table = read_quality_tables(args.picard_metrics_directory).fillna(0)
    base_quality_plot(quality_table)
