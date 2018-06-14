#!python

import sys
import ntpath
import logging
import pandas as pd
from shutil import copyfile

from python_tools.constants import *
from ...util import to_csv, merge_files_across_samples


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

    all_read_counts = merge_files_across_samples(read_counts_files, AGBM_READ_COUNTS_HEADER, SID_COL)
    all_read_counts.columns = AGBM_READ_COUNTS_HEADER
    logging.info(all_read_counts)

    to_csv(all_read_counts, AGBM_READ_COUNTS_FILENAME)


def process_fragment_sizes_files(files):
    """
    Aggregate fragment-sizes metrics files for each Bam into one file
    """
    fragment_sizes_files = [f for f in files if WALTZ_FRAGMENT_SIZES_FILENAME_SUFFIX in f]
    logging.info(fragment_sizes_files)

    all_frag_sizes = merge_files_across_samples(fragment_sizes_files, AGBM_FRAGMENT_SIZES_FILE_HEADER, SID_COL)
    all_frag_sizes.columns = AGBM_FRAGMENT_SIZES_FILE_HEADER
    logging.info(all_frag_sizes)

    to_csv(all_frag_sizes, AGBM_FRAGMENT_SIZES_FILENAME)


def process_intervals_files(files):
    """
    Unique and total coverage, averaged over all intervals, for each sample
    """
    intervals_files = [f for f in files if WALTZ_INTERVALS_FILENAME_SUFFIX in f]
    unique_intervals_files = [f for f in files if WALTZ_INTERVALS_WITHOUT_DUPLICATES_FILENAME_SUFFIX in f]

    coverage_dfs = []
    for files in [intervals_files, unique_intervals_files]:
        columns = [SAMPLE_ID_COLUMN] + WALTZ_INTERVALS_FILE_HEADER
        coverage_df = merge_files_across_samples(files, columns, SID_COL)
        coverage_df.columns = columns

        # New column for average coverage on each interval, times the interval's length
        coverage_df['coverage_X_length'] = coverage_df[WALTZ_FRAGMENT_SIZE_COLUMN] * coverage_df[WALTZ_AVERAGE_COVERAGE_COLUMN]
        # Get the total length of the intervals
        total_intervals_length = coverage_df.drop_duplicates(WALTZ_INTERVAL_NAME_COLUMN)[FRAGMENT_SIZE_COLUMN].sum()
        # Group by sample
        coverage = coverage_df['coverage_X_length'].groupby(coverage_df[SAMPLE_ID_COLUMN])
        # average_coverage = sum(coverage over all intervals) / total length of intervals
        average_coverage = coverage.apply(lambda x: x.sum() / total_intervals_length).to_frame()
        coverage_dfs.append(average_coverage)

    coverage_df = coverage_dfs[0].merge(coverage_dfs[1], left_index=True, right_index=True)
    coverage_df.reset_index(level=0, inplace=True)
    coverage_df.columns = AGBM_COVERAGE_HEADER
    to_csv(coverage_df, AGBM_COVERAGE_FILENAME)


def main():
    """
    Main - called from aggregate_bam_metrics.cwl
    """
    waltz_dir = sys.argv[1]
    files = [os.path.join(waltz_dir, f) for f in os.listdir(waltz_dir)]

    # Todo: Try removing this:
    for input_file in files:
        copyfile(input_file, ntpath.basename(input_file))

    process_read_counts_files(files)
    process_fragment_sizes_files(files)
    process_intervals_files(files)
