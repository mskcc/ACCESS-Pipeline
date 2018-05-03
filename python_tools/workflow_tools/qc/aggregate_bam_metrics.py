#!python

import os
import sys
import ntpath
import pandas as pd
from shutil import copyfile

from ...util import to_csv, merge_files_across_samples
from python_tools.constants import *


# Aggregate Metrics across Bams from multiple samples

# Example Waltz CountReads output files:
#
# Sample_ID_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR.bam.covered-regions
# Sample_ID_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR.bam.fragment-sizes
# Sample_ID_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR.bam.read-counts
#
# Example Waltz PileupMetrics output files:
#
# Sample_ID_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR-pileup.txt
# Sample_ID_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR-pileup-without-duplicates.txt
# Sample_ID_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR-intervals.txt
# Sample_ID_5500-DY-1_L000_mrg_cl_aln_srt_MD_IR_FX_BR-intervals-without-duplicates.txt


# Todo: shouldn't be global
TITLE_FILE = pd.read_csv(sys.argv[2], sep='\t')
SID_COL = TITLE_FILE[TITLE_FILE__SAMPLE_ID_COLUMN]


def process_read_counts_files(files):
    """
    Aggregate read-counts metrics files for each Bam into one file
    """
    read_counts_files = [f for f in files if WALTZ_READ_COUNTS_FILENAME_SUFFIX in f]
    all_read_counts = merge_files_across_samples(read_counts_files, SID_COL)
    all_read_counts.columns = AGBM_READ_COUNTS_HEADER
    to_csv(all_read_counts, AGBM_READ_COUNTS_FILENAME)


def process_fragment_sizes_files(files):
    """
    Aggregate fragment-sizes metrics files for each Bam into one file
    """
    fragment_sizes_files = [f for f in files if WALTZ_FRAGMENT_SIZES_FILENAME_SUFFIX in f]
    all_frag_sizes = merge_files_across_samples(fragment_sizes_files, SID_COL)
    all_frag_sizes.columns = AGBM_FRAGMENT_SIZES_FILE_HEADER
    to_csv(all_frag_sizes, AGBM_FRAGMENT_SIZES_FILENAME)


def create_waltz_coverage_file(files):
    """
    Unique and total coverage, averaged over all intervals, for each sample
    """
    input_files = [f for f in files if WALTZ_INTERVALS_FILENAME_SUFFIX in f]
    unique_input_files = [f for f in files if WALTZ_INTERVALS_WITHOUT_DUPLICATES_FILENAME_SUFFIX in f]

    coverage_dfs = []
    for files in [input_files, unique_input_files]:
        coverage_df = merge_files_across_samples(files, SID_COL)

        coverage_df.columns = [SAMPLE_ID_COLUMN] + WALTZ_INTERVALS_FILE_HEADER
        coverage_df['coverage_X_length'] = coverage_df[WALTZ_AVERAGE_COVERAGE_COLUMN] * coverage_df[WALTZ_FRAGMENT_SIZE_COLUMN]

        coverage_avg = coverage_df.groupby(SAMPLE_ID_COLUMN, as_index=False).mean()
        coverage_per_sample = coverage_avg[[SAMPLE_ID_COLUMN, 'coverage_X_length']]
        coverage_per_sample.columns = [SAMPLE_ID_COLUMN, WALTZ_AVERAGE_COVERAGE_COLUMN]
        coverage_dfs.append(coverage_per_sample)

    coverage_df = coverage_dfs[0].merge(
        coverage_dfs[1],
        on=[SAMPLE_ID_COLUMN],
        suffixes=('_total', '_unique')
    )

    coverage_df = coverage_df[AGBM_COVERAGE_HEADER]
    coverage_df.columns = AGBM_COVERAGE_HEADER
    to_csv(coverage_df, AGBM_COVERAGE_FILENAME)


def create_sum_of_coverage_dup_temp_file(files):
    """
    Duplicate coverage temp file
    """
    input_files = [f for f in files if WALTZ_INTERVALS_FILENAME_SUFFIX in f]

    intervals_coverage_all = merge_files_across_samples(input_files, SID_COL)
    intervals_coverage_all.columns = [SAMPLE_ID_COLUMN] + WALTZ_INTERVALS_FILE_HEADER

    # Todo: is interval_name the same as 0:5 for key?
    togroupby = [SAMPLE_ID_COLUMN, WALTZ_INTERVAL_NAME_COLUMN]
    gc_coverage_sum_per_interval = intervals_coverage_all.groupby(togroupby).sum().reset_index()

    # Todo: should 'gc' be averaged across all samples or come from just last sample?
    # gc[key] = line_split[7]

    to_csv(gc_coverage_sum_per_interval, 't5')


def create_sum_of_coverage_nodup_temp_file(files):
    """
    Non-duplicate coverage temp file
    """
    input_files = [f for f in files if WALTZ_INTERVALS_WITHOUT_DUPLICATES_FILENAME_SUFFIX in f]

    intervals_coverage_all = merge_files_across_samples(input_files, SID_COL)
    intervals_coverage_all.columns = [SAMPLE_ID_COLUMN] + WALTZ_INTERVALS_FILE_HEADER

    togroupby = [SAMPLE_ID_COLUMN, INTERVAL_NAME_COLUMN]
    gc_coverage_sum_per_interval = intervals_coverage_all.groupby(togroupby).sum().reset_index()

    to_csv(gc_coverage_sum_per_interval, 't6')


def create_intervals_coverage_sum_file():
    """
    Unique and total coverage, averaged over all intervals, for each sample?
    """
    t5 = pd.read_csv('t5', sep='\t')
    t6 = pd.read_csv('t6', sep='\t')
    t6 = t6[[SAMPLE_ID_COLUMN, INTERVAL_NAME_COLUMN, WALTZ_AVERAGE_COVERAGE_COLUMN]]

    intervals_coverage_sum = t5.merge(t6, on=[SAMPLE_ID_COLUMN, WALTZ_INTERVAL_NAME_COLUMN], suffixes=('_total', '_unique'))
    to_csv(intervals_coverage_sum, AGBM_INTERVALS_COVERAGE_SUM_FILENAME)


def main():
    """
    Main - called from aggregate-bam-metrics.cwl
    """
    files = [os.path.join(sys.argv[1], f) for f in os.listdir(sys.argv[1])]

    for input_file in files:
        copyfile(input_file, ntpath.basename(input_file))

    process_read_counts_files(files)
    process_fragment_sizes_files(files)
    create_waltz_coverage_file(files)
    create_sum_of_coverage_dup_temp_file(files)
    create_sum_of_coverage_nodup_temp_file(files)
    create_intervals_coverage_sum_file()


if __name__ == '__main__':
    main()
