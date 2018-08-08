#!python

##################################################
# ACCESS QC Module
# Innovation Laboratory
# Center For Molecular Oncology
# Memorial Sloan Kettering Cancer Research Center
# maintainer: Ian Johnson (johnsoni@mskcc.org)
##################################################

import re
import logging
import numpy as np
import pandas as pd

from ...constants import *


#####################
# Helper methods
# todo: refactor away
#####################

def unique_or_tot(x):
    if TOTAL_LABEL in x:
        return TOTAL_LABEL
    else:
        return PICARD_LABEL


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
    read_counts = pd.melt(read_counts, id_vars=[TITLE_FILE__SAMPLE_ID_COLUMN], var_name='Category')
    # We only want the read counts-related row values
    read_counts = read_counts[~read_counts['Category'].isin(['bam', TOTAL_READS_COLUMN, UNMAPPED_READS_COLUMN, 'duplicate_fraction'])]
    read_counts['method'] = read_counts['Category'].apply(unique_or_tot)
    read_counts['pool'] = pool
    # read_counts = read_counts.reset_index(drop=True)

    return read_counts


def get_read_counts_total_table(path, pool):
    """
    This table is used for "Fraction of Total Reads that Align to the Human Genome" plot
    """
    full_path = os.path.join(path, AGBM_READ_COUNTS_FILENAME)
    read_counts_total = pd.read_csv(full_path, sep='\t')

    col_idx = ~read_counts_total.columns.str.contains(PICARD_LABEL)

    read_counts_total = read_counts_total.iloc[:, col_idx]
    read_counts_total['AlignFrac'] = read_counts_total[TOTAL_MAPPED_COLUMN] / read_counts_total[TOTAL_READS_COLUMN]
    read_counts_total[TOTAL_OFF_TARGET_FRACTION_COLUMN] = 1 - read_counts_total[TOTAL_ON_TARGET_FRACTION_COLUMN]

    read_counts_total['pool'] = pool
    return read_counts_total


def get_coverage_table(path, pool):
    """
    Coverage table
    """
    full_path = os.path.join(path, AGBM_COVERAGE_FILENAME)
    coverage_table = pd.read_csv(full_path, sep='\t')
    coverage_table = pd.melt(coverage_table, id_vars=SAMPLE_ID_COLUMN, var_name='method', value_name='average_coverage')
    coverage_table['method'] = coverage_table['method'].str.replace('average_coverage_', '')
    coverage_table['pool'] = pool
    return coverage_table


def get_collapsed_waltz_tables(path, method, pool):
    """
    Creates read_counts, coverage, and gc_bias tables for collapsed bam metrics.
    """
    read_counts_table_path = os.path.join(path, AGBM_READ_COUNTS_FILENAME)
    read_counts_table = pd.read_csv(read_counts_table_path, sep='\t')
    read_counts_table = pd.melt(read_counts_table, id_vars=[TITLE_FILE__SAMPLE_ID_COLUMN], var_name='Category')
    read_counts_table = read_counts_table.dropna(axis=0)
    read_counts_table['method'] = [method] * len(read_counts_table)
    read_counts_table['pool'] = pool

    # Todo: merge with get_cov_table
    coverage_table_path = '/'.join([path, AGBM_COVERAGE_FILENAME])
    coverage_table = pd.read_csv(coverage_table_path, sep='\t', usecols=[0, 1], names=[SAMPLE_ID_COLUMN, 'average_coverage'], header=0)
    coverage_table['method'] = [method] * len(coverage_table)
    coverage_table['pool'] = pool

    gc_bias_table = get_gc_table(method, WALTZ_INTERVALS_FILENAME_SUFFIX, path)

    return [read_counts_table, coverage_table, gc_bias_table]


def get_gc_table(curr_method, intervals_filename_suffix, path):
    """
    Function to create GC content table
    """
    gc_with_cov = pd.DataFrame(columns=GC_BIAS_HEADER)
    sample_files = [f for f in os.listdir(path) if intervals_filename_suffix in f]

    logging.info(curr_method, intervals_filename_suffix, path)
    logging.info(sample_files)
    logging.info(os.listdir(path))

    for sample in sample_files:
        filename = '/'.join([path, sample])
        curr_table = pd.read_csv(filename, sep='\t')

        # todo - consolidate / standardize sample names
        sample = sample.replace(intervals_filename_suffix, '')

        # todo - columns should be given constant labels:
        newDf = pd.DataFrame({
            'method': [curr_method] * len(curr_table),
            'Sample': [sample] * len(curr_table),
            'interval_name': curr_table.ix[:, 3],
            'coverage': curr_table.ix[:, 5],
            'gc': curr_table.ix[:, 7]
        })

        gc_with_cov = pd.concat([gc_with_cov, newDf]).sort_values(['Sample', 'interval_name'])

    return gc_with_cov


def get_bins(tbl):
    """
    Create bins from min_gc value to max_gc value in increments of 0.05 (for GC content table)
    """
    logging.info('GC table generation')
    logging.info(tbl)

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


# def get_gc_table_average_for_each_sample(tbl):
#     """
#     Creates the GC content table, with each sample represented
#     """
#     all_bins = get_bins(tbl)
#     tbl['gc_bin'] = pd.cut(tbl['gc'], all_bins)
#     means = tbl.groupby(['gc_bin', 'method', SAMPLE_ID_COLUMN]).mean()
#     tbl['coverage_norm'] = np.divide(tbl['coverage'], means['coverage'] + EPSILON)
#     return tbl
# Todo: replace v with ^

def get_gc_table_average_for_each_sample(tbl):
    """
    Creates the GC content table, with each sample represented
    """
    final_bins_table = pd.DataFrame(columns=GC_BIAS_AVERAGE_COVERAGE_EACH_SAMPLE_HEADER)
    all_samples = tbl['Sample'].unique()
    all_methods = tbl['method'].unique()
    minGC = np.min(tbl['gc'])
    maxGC = np.max(tbl['gc'])

    low_bin = round(minGC - np.mod(minGC, 0.05), 2)
    high_bin = round(maxGC + 0.1 - np.mod(maxGC, 0.05), 2)

    all_bins = np.arange(low_bin, high_bin, 0.05)

    for method in all_methods:
        for sample in all_samples:
            method_boolv = (tbl['method'] == method)
            sample_boolv = (tbl['Sample'] == sample)
            curr_table = tbl[method_boolv & sample_boolv].copy()
            curr_table['coverage_norm'] = curr_table['coverage'] / np.mean(curr_table['coverage'])

            for subset in range(0, len(all_bins) - 1):
                low_bin_boolv = (curr_table['gc'] >= all_bins[subset])
                high_bin_boolv = (curr_table['gc'] < all_bins[subset + 1])

                cur_gc_values = curr_table[low_bin_boolv & high_bin_boolv]['coverage_norm']
                avg_cov = np.mean(cur_gc_values)

                newDf = pd.DataFrame({
                    'method': [method.replace('Waltz', '')],
                    'Sample': [sample],
                    'gc_bin': [all_bins[subset]],
                    'coverage': [avg_cov]
                })
                final_bins_table = pd.concat([final_bins_table, newDf])

    # Restrict to .3 < GC content < .8
    low_gc_boolv = (final_bins_table['gc_bin'] >= .3)
    high_gc_boolv = (final_bins_table['gc_bin'] <= .8)
    final_bins_table = final_bins_table[low_gc_boolv & high_gc_boolv]

    return final_bins_table


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


def get_coverage_per_interval(tbl):
    """
    Creates table of (un-collapsed) coverage per interval
    """
    total_boolv = (tbl['method'] == UNFILTERED_COLLAPSING_METHOD)
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
    read_counts_total_filename = '/'.join([output_dir, 'read-counts-total.txt'])
    coverage_per_interval_filename = '/'.join([output_dir, 'coverage-per-interval.txt'])

    read_counts_total_pool_a_table = get_read_counts_total_table(args.standard_waltz_pool_a, POOL_A_LABEL)
    read_counts_total_pool_b_table = get_read_counts_total_table(args.standard_waltz_pool_b, POOL_B_LABEL)
    read_counts_total_table = pd.concat([read_counts_total_pool_a_table, read_counts_total_pool_b_table])

    # Std, Pool A and B
    read_counts_table = get_read_counts_table(args.standard_waltz_pool_a, POOL_A_LABEL)
    coverage_table = get_coverage_table(args.standard_waltz_pool_a, POOL_A_LABEL)
    # GC Bias & Coverage Distribution per Interval graphs come from Standard Bam, A Targets
    gc_cov_int_table = get_gc_table(TOTAL_LABEL, WALTZ_INTERVALS_FILENAME_SUFFIX, args.standard_waltz_pool_a)

    read_counts_table = pd.concat([get_read_counts_table(args.standard_waltz_pool_b, POOL_B_LABEL), read_counts_table])
    coverage_table = pd.concat([get_coverage_table(args.standard_waltz_pool_b, POOL_B_LABEL), coverage_table])


    ###### Pool A #######
    # Add in the Marianas Unfiltered tables
    mw = get_collapsed_waltz_tables(args.unfiltered_waltz_pool_a, UNFILTERED_COLLAPSING_METHOD, POOL_A_LABEL)
    read_counts_table = pd.concat([read_counts_table, mw[0]])
    coverage_table = pd.concat([coverage_table, mw[1]])
    gc_cov_int_table = pd.concat([gc_cov_int_table, mw[2]])

    # Add in the Marianas Simplex tables
    mw = get_collapsed_waltz_tables(args.simplex_waltz_pool_a, SIMPLEX_COLLAPSING_METHOD, POOL_A_LABEL)
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

    # Add in the Marianas Simplex tables
    mw = get_collapsed_waltz_tables(args.simplex_waltz_pool_b, SIMPLEX_COLLAPSING_METHOD, POOL_B_LABEL)
    read_counts_table = pd.concat([read_counts_table, mw[0]])
    coverage_table = pd.concat([coverage_table, mw[1]])

    # Add in the Marianas Duplex tables
    mw = get_collapsed_waltz_tables(args.duplex_waltz_pool_b, DUPLEX_COLLAPSING_METHOD, POOL_B_LABEL)
    read_counts_table = pd.concat([read_counts_table, mw[0]])
    coverage_table = pd.concat([coverage_table, mw[1]])


    # Use base tables to create additional tables
    gc_avg_table_all = get_gc_table_average_over_all_samples(gc_cov_int_table)
    gc_avg_table_each = get_gc_table_average_for_each_sample(gc_cov_int_table)
    coverage_per_interval_table = get_coverage_per_interval(gc_cov_int_table)

    # Write all tables
    read_counts_table.to_csv(read_counts_filename, sep='\t', index=False)
    read_counts_total_table.to_csv(read_counts_total_filename, sep='\t', index=False)
    coverage_table.to_csv(coverage_agg_filename, sep='\t', index=False)
    gc_cov_int_table.to_csv(gc_bias_with_coverage_filename, sep='\t', index=False)
    gc_avg_table_each.to_csv(each_sample_coverage_filename, sep='\t', index=False)
    gc_avg_table_all.to_csv(all_samples_coverage_filename, sep='\t', index=False)
    coverage_per_interval_table.to_csv(coverage_per_interval_filename, sep='\t', index=False)

    # Fragment Sizes graph comes from Unfiltered Bam, Pool A Targets
    # todo: not clean
    import shutil
    frag_sizes_path = os.path.join(args.unfiltered_waltz_pool_a, 'fragment-sizes.txt')
    shutil.copyfile(frag_sizes_path, '%s/%s' % (output_dir, frag_sizes_path.split('/')[-1]))
