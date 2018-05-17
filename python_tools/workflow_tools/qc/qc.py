#!python

#######################################################
# Innovation-QC Module
# Innovation Laboratory
# Center For Molecular Oncology
# Memorial Sloan Kettering Cancer Research Center
# maintainer: Ian Johnson (johnsoni@mskcc.org)
#######################################################

import re
import numpy as np
import pandas as pd

from ...util import merge_files_across_samples
from ...constants import *


#####################
# Helper methods
# todo: refactor away
#####################

def unique_or_tot(x):
    if 'total' in x:
        return 'total'
    else:
        return 'picard'


def get_gene_and_probe(interval):
    # todo - should be more specific
    interval_regex = re.compile(r'^.*_.*_.*_.*$')

    # Example interval string: exon_AKT1_4a_1
    if interval[0:4] == 'exon':
        split = interval.split('_')
        return split[1], split[2] + '_' + split[3]

    # Another example I've encountered: 426_2903_324(APC)_1a
    elif interval_regex.match(interval):
        split = interval.split('_')
        return '_'.join(split[0:2]), '_'.join(split[2:4])

    else:
        curr = interval.split('_exon_')
        return curr[0], curr[1]


##########################
# Table creation methods #
##########################

def get_read_counts_table(path, pool):
    """
    This method is only used to generate stats for un-collapsed bams
    """
    read_counts_path = os.path.join(path, AGBM_READ_COUNTS_FILENAME)
    read_counts = pd.read_csv(read_counts_path, sep='\t')
    # Melt our DF to get all values of the on target rate and duplicate rates as values
    read_counts = pd.melt(read_counts, id_vars=[SAMPLE_ID_COLUMN], var_name='Category')
    # We only want the read counts-related row values
    read_counts = read_counts[~read_counts['Category'].isin(['bam', TOTAL_READS_COLUMN, UNMAPPED_READS_COLUMN, 'duplicate_fraction'])]
    read_counts['method'] = read_counts['Category'].apply(unique_or_tot)
    read_counts['pool'] = pool
    # read_counts = read_counts.reset_index(drop=True)

    return read_counts


def get_read_counts_total_table(path):
    """
    This table is used for "Fraction of Total Reads that Align to the Human Genome" plot
    """
    full_path = os.path.join(path, AGBM_READ_COUNTS_FILENAME)
    read_counts_total = pd.read_csv(full_path, sep='\t')

    col_idx = ~read_counts_total.columns.str.contains('unique')

    read_counts_total = read_counts_total.iloc[:, col_idx]
    read_counts_total[TOTAL_ON_TARGET_FRACTION_COLUMN] = read_counts_total[TOTAL_MAPPED_COLUMN] / read_counts_total[TOTAL_READS_COLUMN]
    read_counts_total[TOTAL_OFF_TARGET_FRACTION_COLUMN] = 1 - read_counts_total[TOTAL_ON_TARGET_FRACTION_COLUMN]

    return read_counts_total


def get_coverage_table(path, pool):
    """
    Coverage table
    """
    full_path = os.path.join(path, AGBM_COVERAGE_FILENAME)
    coverage_table = pd.read_csv(full_path, sep='\t')
    coverage_table = pd.melt(coverage_table, id_vars=SAMPLE_ID_COLUMN, var_name='method', value_name='average_coverage')
    coverage_table['pool'] = pool * len(coverage_table)
    return coverage_table


def get_collapsed_waltz_tables(path, method, pool):
    """
    Creates read_counts, coverage, and gc_bias tables for collapsed bam metrics.
    """
    read_counts_table_path = os.path.join(path, AGBM_READ_COUNTS_FILENAME)
    read_counts_table = pd.read_csv(read_counts_table_path, sep='\t')
    read_counts_table = pd.melt(read_counts_table, id_vars=[SAMPLE_ID_COLUMN], var_name='Category')
    read_counts_table = read_counts_table.dropna(axis=0)
    read_counts_table['method'] = [method] * len(read_counts_table)
    read_counts_table['pool'] = [pool] * len(read_counts_table)

    coverage_table_path = '/'.join([path, AGBM_COVERAGE_FILENAME])
    coverage_table = pd.read_csv(coverage_table_path, sep='\t', usecols=[0, 1], names=[SAMPLE_ID_COLUMN, 'average_coverage'], header=0)
    coverage_table['method'] = [method] * len(coverage_table)
    if POOL_A_LABEL in method:
        coverage_table['pool'] = POOL_A_LABEL * len(coverage_table)
    elif POOL_B_LABEL in method:
        coverage_table['pool'] = POOL_B_LABEL * len(coverage_table)

    gc_bias_table = get_gc_table(method, WALTZ_INTERVALS_FILENAME_SUFFIX, path)

    return [read_counts_table, coverage_table, gc_bias_table]


def get_table_duplication(read_counts_table):
    """
    Creates duplication rate table
    """
    mapped_boolv = read_counts_table['Category'] == TOTAL_MAPPED_COLUMN

    total_method_boolv = read_counts_table['method'] == TOTAL_LABEL

    for pool in ['pool_a', 'pool_b']:
        pool_boolv = read_counts_table['pool'] == pool
        rows_idx = mapped_boolv & total_method_boolv & pool_boolv
        mapped_reads = read_counts_table[mapped_boolv][[SAMPLE_ID_COLUMN, 'method', 'value', 'pool']]
        mapped_reads['value'] = mapped_reads['value'].astype(int)
        mapped_reads_total = read_counts_table[rows_idx][[SAMPLE_ID_COLUMN, 'value']]
        mapped_reads_total['value'] = mapped_reads_total['value'].astype(int)

        grouped = mapped_reads.groupby(['method', 'pool'])
        unique_rate = grouped['value'].transform(lambda x: x.div(mapped_reads_total['value'].values))
        dup_rate_table = mapped_reads.copy()
        dup_rate_table['unique_rate'] = unique_rate
        dup_rate_table['duplication_rate'] = 1 - dup_rate_table['unique_rate']

    dup_rate_table = dup_rate_table[DUPLICATION_RATES_HEADER]

    return dup_rate_table


def get_gc_table(curr_method, intervals_filename_suffix, path):
    """
    Function to create GC content table
    """
    sample_files = [f for f in os.listdir(path) if intervals_filename_suffix in f]

    for i, sample in enumerate(sample_files):
        sample_files[i] = '/'.join([path, sample])

    gc_with_cov = merge_files_across_samples(sample_files)
    gc_with_cov = gc_with_cov.ix[:, [SAMPLE_ID_COLUMN, 3, 5, 7]]
    gc_with_cov['method'] = [curr_method] * len(gc_with_cov)
    gc_with_cov.columns = GC_BIAS_HEADER

    return gc_with_cov


def get_bins(tbl):
    min_gc = np.min(tbl['gc'])
    max_gc = np.max(tbl['gc'])
    start = round(min_gc - np.mod(min_gc, 0.05), 2)
    stop = round(max_gc + 0.1 - np.mod(max_gc, 0.05), 2)
    all_bins = np.arange(start, stop, step=0.05)
    return all_bins


def get_gc_table_average_over_all_samples(tbl):
    """
    Function to create GC content table: averaged over all samples
    """
    all_bins = get_bins(tbl)
    tbl['gc_bin'] = pd.cut(tbl['gc'], all_bins)
    means = tbl.groupby(['gc_bin', 'method']).transform(np.mean)
    tbl['coverage_norm'] = np.divide(tbl['coverage'], means['coverage'] + EPSILON)
    return tbl


def get_gc_table_average_for_each_sample(tbl):
    """
    Creates the GC content table, with each sample represented
    """
    all_bins = get_bins(tbl)
    tbl['gc_bin'] = pd.cut(tbl['gc'], all_bins)
    means = tbl.groupby(['gc_bin', 'method', SAMPLE_ID_COLUMN]).transform(np.mean)
    tbl['coverage_norm'] = np.divide(tbl['coverage'], means['coverage'] + EPSILON)
    return tbl


def get_gc_coverage_table(std_waltz_path):
    total_gc_table = get_gc_table(TOTAL_LABEL, WALTZ_INTERVALS_FILENAME_SUFFIX, std_waltz_path)
    picard_gc_table = get_gc_table(PICARD_LABEL, WALTZ_INTERVALS_WITHOUT_DUPLICATES_FILENAME_SUFFIX, std_waltz_path)
    gc_cov_int_table = pd.concat([total_gc_table, picard_gc_table])
    gc_cov_int_table = gc_cov_int_table.sort_values(['method'], ascending=False)
    return gc_cov_int_table


def get_coverage_per_interval(tbl):
    """
    Creates table of (un-collapsed) coverage per interval
    """
    total_boolv = (tbl['method'] == 'total')
    # todo - why is this needed:
    exon_boolv = ['exon' in y for y in tbl['interval_name']]
    relevant_coverage_columns = ['coverage', 'interval_name', SAMPLE_ID_COLUMN]
    final_tbl = tbl[total_boolv & exon_boolv][relevant_coverage_columns]

    gene_probe = [get_gene_and_probe(val) for val in final_tbl['interval_name']]
    gene_probe_df = pd.DataFrame(gene_probe, columns=['Gene', 'Probe'])

    # Todo: most likely, the reset_index() calls are unnecessary
    final_tbl = final_tbl.reset_index()
    final_tbl = pd.concat([final_tbl, gene_probe_df], axis=1)
    final_tbl = final_tbl.reset_index()

    return final_tbl


def get_insert_size_peaks_table(path):
    """
    This table is used for the "Insert Size Distribution for All Samples" plot
    """
    files = [fileName for fileName in os.listdir(path) if WALTZ_FRAGMENT_SIZES_FILENAME_SUFFIX in fileName]

    final_tbl_peaks = pd.DataFrame(columns=INSERT_SIZE_PEAKS_HEADER)
    for f in files:

        cur_sizes = pd.read_csv(path + '/' + f, sep="\t", names=['fragment_size', 'peak_total', 'peak_unique'])
        max_tot = max(cur_sizes['peak_total'])
        max_unique = max(cur_sizes['peak_unique'])
        max_tot_size = cur_sizes['fragment_size'][np.argmax(cur_sizes['peak_total'])]
        max_unique_size = cur_sizes['fragment_size'][np.argmax(cur_sizes['peak_unique'])]

        final_tbl_peaks = pd.concat([final_tbl_peaks, pd.DataFrame({
            SAMPLE_ID_COLUMN: f,
            'peak_total': [max_tot],
            'peak_total_size': [max_tot_size],
            'peak_unique': [max_unique],
            'peak_unique_size': [max_unique_size]
        })])

    return final_tbl_peaks


########
# Main #
########

def main(args):
    output_dir = args.tables_output_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Output file names
    read_counts_filename = '/'.join([output_dir, 'read-counts-agg.txt'])
    coverage_agg_filename = '/'.join([output_dir, 'coverage-agg.txt'])
    all_samples_coverage_filename = '/'.join([output_dir, 'GC-bias-with-coverage-averages-over-all-samples.txt'])
    each_sample_coverage_filename = '/'.join([output_dir, 'GC-bias-with-coverage-averages-over-each-sample.txt'])
    gc_bias_with_coverage_filename = '/'.join([output_dir, 'GC-bias-with-coverage.txt'])
    insert_size_peaks_filename = '/'.join([output_dir, 'insert-size-peaks.txt'])
    read_counts_total_filename = '/'.join([output_dir, 'read-counts-total.txt'])
    coverage_per_interval_filename = '/'.join([output_dir, 'coverage-per-interval.txt'])
    duplication_rates_filename = '/'.join([output_dir, 'duplication-rates.txt'])


    read_counts_total_table = get_read_counts_total_table(args.standard_waltz_pool_a)
    insert_size_peaks_table = get_insert_size_peaks_table(args.unfiltered_waltz_pool_a)

    # Std, Pool A and B
    read_counts_table = get_read_counts_table(args.standard_waltz_pool_a, POOL_A_LABEL)
    coverage_table = get_coverage_table(args.standard_waltz_pool_a, POOL_A_LABEL)
    gc_cov_int_table = get_gc_coverage_table(args.standard_waltz_pool_a)

    read_counts_table = pd.concat([get_read_counts_table(args.standard_waltz_pool_b, POOL_B_LABEL), read_counts_table])
    coverage_table = pd.concat([get_coverage_table(args.standard_waltz_pool_b, POOL_B_LABEL), coverage_table])
    gc_cov_int_table = pd.concat([get_gc_coverage_table(args.standard_waltz_pool_b), gc_cov_int_table])


    ###### Pool A #######
    # Add in the Marianas Unfiltered tables
    mw = get_collapsed_waltz_tables(args.unfiltered_waltz_pool_a, UNFILTERED_COLLAPSING_METHOD, POOL_A_LABEL)
    read_counts_table = pd.concat([read_counts_table, mw[0]])
    coverage_table = pd.concat([coverage_table, mw[1]])
    gc_cov_int_table = pd.concat([gc_cov_int_table, mw[2]])

    # Add in the Marianas Simplex Duplex tables
    mw = get_collapsed_waltz_tables(args.simplex_duplex_waltz_pool_a, SIMPLEX_DUPLEX_COLLAPSING_METHOD, POOL_A_LABEL)
    read_counts_table = pd.concat([read_counts_table, mw[0]])
    coverage_table = pd.concat([coverage_table, mw[1]])
    gc_cov_int_table = pd.concat([gc_cov_int_table, mw[2]])

    # Add in the Marianas Duplex tables
    mw = get_collapsed_waltz_tables(args.duplex_waltz_pool_a, DUPLEX_COLLAPSING_METHOD, POOL_A_LABEL)
    read_counts_table = pd.concat([read_counts_table, mw[0]])
    coverage_table = pd.concat([coverage_table, mw[1]])
    gc_cov_int_table = pd.concat([gc_cov_int_table, mw[2]])

    ###### Pool B #######
    # Add in the Marianas Unfiltered tables
    mw = get_collapsed_waltz_tables(args.unfiltered_waltz_pool_b, UNFILTERED_COLLAPSING_METHOD, POOL_B_LABEL)
    read_counts_table = pd.concat([read_counts_table, mw[0]])
    coverage_table = pd.concat([coverage_table, mw[1]])
    gc_cov_int_table = pd.concat([gc_cov_int_table, mw[2]])

    # Add in the Marianas Simplex Duplex tables
    mw = get_collapsed_waltz_tables(args.simplex_duplex_waltz_pool_b, SIMPLEX_DUPLEX_COLLAPSING_METHOD, POOL_B_LABEL)
    read_counts_table = pd.concat([read_counts_table, mw[0]])
    coverage_table = pd.concat([coverage_table, mw[1]])
    gc_cov_int_table = pd.concat([gc_cov_int_table, mw[2]])

    # Add in the Marianas Duplex tables
    mw = get_collapsed_waltz_tables(args.duplex_waltz_pool_b, DUPLEX_COLLAPSING_METHOD, POOL_B_LABEL)
    read_counts_table = pd.concat([read_counts_table, mw[0]])
    coverage_table = pd.concat([coverage_table, mw[1]])
    gc_cov_int_table = pd.concat([gc_cov_int_table, mw[2]])


    # Use base tables to create additional tables
    gc_avg_table_all = get_gc_table_average_over_all_samples(gc_cov_int_table)
    gc_avg_table_each = get_gc_table_average_for_each_sample(gc_cov_int_table)
    coverage_per_interval_table = get_coverage_per_interval(gc_cov_int_table)
    duplication_table = get_table_duplication(read_counts_table)

    # Write all tables
    read_counts_table.to_csv(read_counts_filename, sep='\t', index=False)
    read_counts_total_table.to_csv(read_counts_total_filename, sep='\t', index=False)
    coverage_table.to_csv(coverage_agg_filename, sep='\t', index=False)
    insert_size_peaks_table.to_csv(insert_size_peaks_filename, sep='\t', index=False)
    gc_cov_int_table.to_csv(gc_bias_with_coverage_filename, sep='\t', index=False)
    gc_avg_table_each.to_csv(each_sample_coverage_filename, sep='\t', index=False)
    gc_avg_table_all.to_csv(all_samples_coverage_filename, sep='\t', index=False)
    coverage_per_interval_table.to_csv(coverage_per_interval_filename, sep='\t', index=False)
    duplication_table.to_csv(duplication_rates_filename, sep='\t', index=False)
