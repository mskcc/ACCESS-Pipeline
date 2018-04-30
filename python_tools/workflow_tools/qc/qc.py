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

from ...constants import *


###################
# Helper methods  #
# todo: refactor away
###################

def unique_or_tot(x):
    if (TOTAL_READS_COLUMN in x) or (UNMAPPED_READS_COLUMN in x) or ('duplicate' in x):
        return None
    elif TOTAL_LABEL in x:
        return TOTAL_LABEL
    else:
        return PICARD_LABEL


def rename_category(y):
    if 'unique' in y:
        return y.replace('unique', '')
    elif 'total' in y:
        return y.replace('total', '')
    else:
        return y


def rename_category_2(y):
    if ('unique' in y) or ('total_reads' in y) or (UNMAPPED_READS_COLUMN in y) or ('duplicate' in y):
        return None
    elif 'total' in y:
        return y.replace('total', '')
    else:
        return y


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

def get_gc_table(curr_method, intervals_filename_suffix, path):
    """
    Function to create GC content table
    """
    gc_with_cov = pd.DataFrame(columns=GC_BIAS_HEADER)
    sample_files = [f for f in os.listdir(path) if intervals_filename_suffix in f]

    for sample in sample_files:
        curr_table = pd.read_table('/'.join([path, sample]), header=None)

        # todo - consolidate / standardize sample names
        sample = sample.replace(intervals_filename_suffix, '')

        # todo - columns should be given constant labels:
        newDf = pd.DataFrame({
            'method': [curr_method.replace('Waltz', '')] * len(curr_table),
            'Sample': [sample] * len(curr_table),
            'interval_name': curr_table.ix[:, 3],
            'coverage': curr_table.ix[:, 5],
            'gc': curr_table.ix[:, 7]
        })

        gc_with_cov = pd.concat([gc_with_cov, newDf]).sort_values(['Sample', 'interval_name'])

    return gc_with_cov


def get_read_counts_table(path):
    """
    This method is only used to generate stats for un-collapsed bams
    """
    read_counts_path = os.path.join(path, AGBM_READ_COUNTS_FILENAME)
    read_counts = pd.read_table(read_counts_path, index_col=0)

    read_counts = pd.melt(read_counts, id_vars=[SAMPLE_ID_COLUMN], var_name='Category')
    read_counts['method'] = read_counts['Category'].apply(unique_or_tot)
    read_counts = read_counts.dropna(axis=0)
    read_counts['Category'] = read_counts['Category'].apply(rename_category)
    read_counts = read_counts.sort_values(['method', 'Category'], ascending=False)
    read_counts = read_counts.reset_index(drop=True).rename(columns={SAMPLE_ID_COLUMN: 'Sample'})

    return read_counts


def get_read_counts_total_table(path):
    """
    This table is used for:
    "Fraction of Total Reads that Align to the Human Genome" plot
    """
    full_path = os.path.join(path, AGBM_READ_COUNTS_FILENAME)
    read_counts_total = pd.read_table(full_path, index_col=0)

    col_idx = ~read_counts_total.columns.str.contains('unique')
    read_counts_total = read_counts_total.iloc[:, col_idx].rename(columns={SAMPLE_ID_COLUMN: 'Sample'})

    read_counts_total[TOTAL_ON_TARGET_FRACTION_COLUMN] = read_counts_total[TOTAL_MAPPED_COLUMN] / read_counts_total[TOTAL_READS_COLUMN]
    read_counts_total[TOTAL_OFF_TARGET_FRACTION_COLUMN] = 1 - read_counts_total[TOTAL_ON_TARGET_FRACTION_COLUMN]

    return read_counts_total


def get_coverage_table(path):
    """
    Coverage table
    """
    full_path = os.path.join(path, AGBM_COVERAGE_FILENAME)
    tbl = pd.read_table(full_path, header=0)
    coverage = pd.melt(tbl, id_vars=SAMPLE_ID_COLUMN, var_name='method', value_name='average_coverage')
    coverage['method'] = coverage['method'].apply(unique_or_tot)
    return coverage


def get_collapsed_waltz_tables(path, method):
    """
    Creates read_counts, coverage, and gc_bias tables for collapsed bam metrics.
    """
    full_path = os.path.join(path, AGBM_READ_COUNTS_FILENAME)
    read_counts_table = pd.read_table(full_path, index_col=0)
    read_counts_table = pd.melt(read_counts_table, id_vars=[SAMPLE_ID_COLUMN], var_name='Category')
    read_counts_table['Category'] = read_counts_table['Category'].apply(rename_category_2)
    read_counts_table = read_counts_table.dropna(axis=0)
    read_counts_table['method'] = [method] * len(read_counts_table)

    read_counts_table = read_counts_table.rename(columns={SAMPLE_ID_COLUMN: 'Sample'})
    read_counts_table['value'] = read_counts_table['value'].astype(float)
    read_counts_table = read_counts_table.sort_values(['method', 'Category'], ascending=False).reset_index(drop=True)

    waltz_coverage_path = '/'.join([path, AGBM_COVERAGE_FILENAME])

    coverage_table = pd.read_table(
        waltz_coverage_path,
        usecols=[0, 1],
        names=[SAMPLE_ID_COLUMN, 'averge_coverage'],
        header=0
    )

    coverage_table['method'] = [method] * len(coverage_table)

    gc_bias_table = get_gc_table(method, WALTZ_INTERVALS_FILENAME_SUFFIX, path)

    return [read_counts_table, coverage_table, gc_bias_table]


def get_table_duplication(tbl):
    """
    Creates duplication rate table
    """
    mapped_idx = tbl['Category'].str.contains('mapped')
    columns_idx = (mapped_idx & tbl['method'].str.contains('total'))
    mapped_reads_total = tbl[columns_idx][[SAMPLE_ID_COLUMN, 'value']]
    methods = tbl['method'].unique().tolist()

    methods.remove('total')
    dup_table = pd.DataFrame(columns=DUPLICATION_RATES_HEADER)

    for method in methods:
        tbl_subset = tbl[mapped_idx & tbl['method'].str.contains(method)]
        unique_counts = tbl_subset['value'].astype('float').values

        # Duplication rate = 1 - (unique mapped reads / total mapped reads)
        duplication_rate = np.subtract(1, np.divide(unique_counts, mapped_reads_total['value'].values))

        new_dup = pd.DataFrame({
            'Sample': mapped_reads_total[SAMPLE_ID_COLUMN].values,
            'method': [method] * (len(mapped_reads_total)),
            'duplication_rate': duplication_rate
        })
        dup_table = pd.concat([dup_table, new_dup])

    return dup_table


def get_gc_table_average_over_all_samples(tbl):
    """
    Function to create GC content table: averaged over all samples
    """
    final_bins_table = pd.DataFrame(columns=GC_BIAS_AVERAGE_COVERAGE_ALL_SAMPLES_HEADER)
    all_samples = tbl[SAMPLE_ID_COLUMN].unique()
    all_methods = tbl['method'].unique()

    min_gc = np.min(tbl['gc'])
    max_gc = np.max(tbl['gc'])

    all_bins = np.arange(round(min_gc - np.mod(min_gc, 0.05), 2), round(max_gc + 0.1 - np.mod(max_gc, 0.05), 2), 0.05)

    for method in all_methods:
        curr_table = tbl[tbl['method'] == method].copy()

        for sample in all_samples:
            curr_loc = curr_table[SAMPLE_ID_COLUMN] == sample

            curr_avg = np.mean(curr_table.loc[curr_loc, 'coverage'])

            if (curr_avg == 0):
                curr_table.loc[curr_loc, 'coverage_norm'] = [0] * len(curr_table.loc[curr_loc, 'coverage'].values)
            else:
                curr_table.loc[curr_loc, 'coverage_norm'] = curr_table.loc[curr_loc, 'coverage'].values / curr_avg

        for bin_idx in range(0, len(all_bins) - 1):

            gt_boolv = (curr_table['gc'] >= all_bins[bin_idx])
            lt_boolv = (curr_table['gc'] < all_bins[bin_idx + 1])

            cur_coverages = curr_table[gt_boolv & lt_boolv]['coverage_norm']
            avg_cov = np.mean(cur_coverages)

            newDf = pd.DataFrame({
                'method': [method],
                'gc_bin': [all_bins[bin_idx]],
                'coverage': [avg_cov]
            })

            final_bins_table = pd.concat([final_bins_table, newDf])

    return final_bins_table


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

    return final_bins_table


def get_coverage_per_interval(tbl):
    """
    Creates table of (un-collapsed) coverage per interval
    """
    total_boolv = (tbl['method'] == 'total')
    # todo - why is this needed:
    exon_boolv = ['exon' in y for y in tbl['interval_name']]
    final_tbl = tbl[total_boolv & exon_boolv][['coverage', 'interval_name', 'Sample']]

    gene_probe = [get_gene_and_probe(val) for val in final_tbl['interval_name']]
    gene_probe_df = pd.DataFrame(gene_probe, columns=['Gene', 'Probe'])

    # todo: most likely, the reset_index() calls are unnecessary
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
            'Sample': f,
            'peak_total': [max_tot],
            'peak_total_size': [max_tot_size],
            'peak_unique': [max_unique],
            'peak_unique_size': [max_unique_size]
        })])

    return final_tbl_peaks


def get_gc_coverage_table(std_waltz_path):
    total_gc_table = get_gc_table(TOTAL_LABEL, WALTZ_INTERVALS_FILENAME_SUFFIX, std_waltz_path)
    picard_gc_table = get_gc_table(PICARD_LABEL, WALTZ_INTERVALS_WITHOUT_DUPLICATES_FILENAME_SUFFIX, std_waltz_path)
    gc_cov_int_table = pd.concat([total_gc_table, picard_gc_table])
    gc_cov_int_table = gc_cov_int_table.sort_values(['method'], ascending=False)
    return gc_cov_int_table


########
# Main #
########

def main(args):
    output_dir = args.tables_output_dir
    std_waltz_path = args.standard_waltz

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

    # Get our 5 base tables
    coverage_table = get_coverage_table(std_waltz_path)
    gc_cov_int_table = get_gc_coverage_table(std_waltz_path)
    read_counts_table = get_read_counts_table(std_waltz_path)
    read_counts_total_table = get_read_counts_total_table(std_waltz_path)
    insert_size_peaks_table = get_insert_size_peaks_table(std_waltz_path)

    # Add in the Marianas Unfiltered tables
    if args.marianas_unfiltered_waltz:
        mw = get_collapsed_waltz_tables(args.marianas_unfiltered_waltz, MARIANAS_UNFILTERED_COLLAPSING_METHOD)
        read_counts_table = pd.concat([read_counts_table, mw[0]])
        coverage_table = pd.concat([coverage_table, mw[1]])
        gc_cov_int_table = pd.concat([gc_cov_int_table, mw[2]])

    # Add in the Marianas Simplex Duplex tables
    if args.marianas_simplex_duplex_waltz:
        mw = get_collapsed_waltz_tables(args.marianas_simplex_duplex_waltz, MARIANAS_SIMPLEX_DUPLEX_COLLAPSING_METHOD)
        read_counts_table = pd.concat([read_counts_table, mw[0]])
        coverage_table = pd.concat([coverage_table, mw[1]])
        gc_cov_int_table = pd.concat([gc_cov_int_table, mw[2]])

    # Add in the Marianas Duplex tables
    if args.marianas_duplex_waltz:
        mw = get_collapsed_waltz_tables(args.marianas_duplex_waltz, MARIANAS_DUPLEX_COLLAPSING_METHOD)
        read_counts_table = pd.concat([read_counts_table, mw[0]])
        coverage_table = pd.concat([coverage_table, mw[1]])
        gc_cov_int_table = pd.concat([gc_cov_int_table, mw[2]])

    # Use base tables for additional tables
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
