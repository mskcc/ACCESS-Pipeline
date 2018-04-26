#!/opt/common/CentOS_6-dev/python/python-2.7.10/bin/python

#######################################################
# Innovation-QC Module
# Innovation Laboratory
# Center For Molecular Oncology
# Memorial Sloan Kettering Cancer Research Center
# maintainer: Ian Johnson (johnsoni@mskcc.org)
#######################################################

import os
import re
import numpy as np
import pandas as pd


#############
# Constants #
#############

# Input file names (Waltz results files)

WALTZ_READ_COUNTS_FILENAME = 'read-counts.txt'
# Example:

# Bam	ID	TotalReads	UnmappedReads	TotalMapped	UniqueMapped	DuplicateFraction	TotalOnTarget	UniqueOnTarget	TotalOnTargetFraction	UniqueOnTargetFraction

# Sample_TD-grail-116-10ng-S_IGO_05500_EM_5_md.bam	Sample_TD-grail-116-10ng-S_IGO_05500_EM_5_md.bam	88787997	115131	88672866	14795184	0.833148688348474	40992391	5791633	0.46	0.39
# Sample_TD-grail-116-10ng_IGO_05500_EM_6_md.bam	Sample_TD-grail-116-10ng_IGO_05500_EM_6_md.bam	101821814	132324	101689490	10782878	0.8939627094206097	46467687	3592360	0.46	0.33
# Sample_TD-grail-116-30ng_IGO_05500_EM_4_md.bam	Sample_TD-grail-116-30ng_IGO_05500_EM_4_md.bam	96600697	114995	96485702	16315974	0.8308974940141908	45049721	6333283	0.47	0.39
# Sample_TD-grail-162-10ng-S_IGO_05500_EM_2_md.bam	Sample_TD-grail-162-10ng-S_IGO_05500_EM_2_md.bam	84116998	324245	83792753	16084241	0.8080473498704596	36873476	6098623	0.44	0.38
# Sample_TD-grail-162-10ng_IGO_05500_EM_3_md.bam	Sample_TD-grail-162-10ng_IGO_05500_EM_3_md.bam	91314251	259866	91054385	11724297	0.8712385240974392	39525456	3923661	0.43	0.33
# Sample_TD-grail-162-30ng_IGO_05500_EM_1_md.bam	Sample_TD-grail-162-30ng_IGO_05500_EM_1_md.bam	108586679	301767	108284912	21003178	0.806037816237963	48133753	7740668	0.44	0.37

WALTZ_COVERAGE_FILENAME = 'waltz-coverage.txt'
# Example:

# Sample	TotalCoverage	UniqueCoverage

# Sample_TD-grail-116-10ng_IGO_05500_EM_6_md	8690.21007316	634.070001628
# Sample_TD-grail-116-10ng-S_IGO_05500_EM_5_md	7536.98270638	1030.72176591
# Sample_TD-grail-116-30ng_IGO_05500_EM_4_md	8267.92405878	1122.17545965
# Sample_TD-grail-162-10ng_IGO_05500_EM_3_md	7807.64015293	736.131411586
# Sample_TD-grail-162-30ng_IGO_05500_EM_1_md	9362.40273715	1465.40464612
# Sample_TD-grail-162-10ng-S_IGO_05500_EM_2_md	7218.55455658	1164.79745506


# Input file prefixes
INTERVALS_WITHOUT_DUPLICATES_FILENAME_SUFFIX = '-intervals-without-duplicates.txt'
INTERVALS_FILENAME_SUFFIX = '-intervals.txt'
FRAGMENT_SIZES_FILENAME_SUFFIX = '.fragment-sizes'

# Labels for collapsing methods
TOTAL_LABEL = 'Total'
PICARD_LABEL = 'Picard'
MARIANAS_UNFILTERED_WALTZ_COLLAPSING_METHOD = 'marianas_unfiltered'
MARIANAS_SIMPLEX_DUPLEX_WALTZ_COLLAPSING_METHOD = 'marianas_simplex_duplex'
MARIANAS_DUPLEX_WALTZ_COLLAPSING_METHOD = 'marianas_duplex'

# Headers for tables
INSERT_SIZE_PEAKS_HEADER = ['Sample', 'PeakTotal', 'PeakTotalSize', 'PeakUnique', 'PeakUniqueSize']
DUPLICATION_RATES_HEADER = ['Sample', 'Method', 'DuplicationRate']
GC_BIAS_AVERAGE_COVERAGE_EACH_SAMPLE_HEADER = ['Method', 'Sample', 'GCbin', 'Coverage']
GC_BIAS_HEADER = ['Method', 'Sample', 'Interval', 'Coverage', 'GC']
GC_BIAS_AVERAGE_COVERAGE_ALL_SAMPLES_HEADER = ['Method', 'GCbin', 'Coverage']



###################
# Helper methods  #
###################
# todo - refactor these away

def fix_sample_names(table):
    if 'ID' in table.columns:
        table['ID'] = table['ID'].apply(change_sample_name)
    if 'Sample' in table.columns:
        table['Sample'] = table['Sample'].apply(change_sample_name)
    if 'SampleID' in table.columns:
        table['SampleID'] = table['Sample_ID'].apply(change_sample_name)
    if 'Sample_ID' in table.columns:
        table['Sample_ID'] = table['Sample_ID'].apply(change_sample_name)
    return table


def change_sample_name(name):
    new_name = name.replace('Sample_', '')
    new_name = new_name.split('-IGO-')[0]
    new_name = new_name.split('_IGO_')[0]
    new_name = re.sub(r'_standard.*', '', new_name)

    # Ex: ZS-msi-4506-pl-T01_IGO_05500_EF_41_S41
    #                                       ^^^^
    new_name = re.sub(r'_.\d\d$', '', new_name)
    return new_name


def unique_or_tot(x):
    if ('TotalReads' in x) or ('UnmappedReads' in x) or ('Duplicates' in x):
        return None
    elif 'Total' in x:
        return 'Total'
    else:
        return 'Picard'


def rename_category(y):
    if 'Unique' in y:
        return y.replace('Unique', '')
    elif 'Total' in y:
        return y.replace('Total', '')
    else:
        return y


def rename_category_2(y):
    if ('Unique' in y) or ('TotalReads' in y) or ('UnmappedReads' in y) or ('Duplicates' in y):
        return None
    elif 'Total' in y:
        return y.replace('Total', '')
    else:
        return y


##########################
# Table creation methods #
##########################

def get_gc_table(curr_method, intervals_filename_suffix, path):
    '''
    Function to create GC content table

    <sample>-intervals.txt has the following columns:
    3: Interval
    5: Coverage
    7: GC

    :param currMethod:
    :param intervals_filename_suffix: either INTERVALS_FILENAME_SUFFIX or INTERVALS_WITHOUT_DUPLICATES_FILENAME_SUFFIX
    :param path:
    :return:
    '''
    GCwithCov = pd.DataFrame(columns=GC_BIAS_HEADER)
    sampleFiles = [f for f in os.listdir(path) if intervals_filename_suffix in f]

    for sample in sampleFiles:
        currTable = pd.read_table('/'.join([path, sample]), header=None)

        # todo - consolidate / standardize sample names
        sample = sample.replace(intervals_filename_suffix, '')

        # todo - columns should be given constant labels:
        newDf = pd.DataFrame({
            'Method': [curr_method.replace('Waltz', '')] * len(currTable),
            'Sample': [sample] * len(currTable),
            'Interval': currTable.ix[:, 3],
            'Coverage': currTable.ix[:, 5],
            'GC': currTable.ix[:, 7]
        })

        GCwithCov = pd.concat([GCwithCov, newDf]).sort_values(['Sample', 'Interval'])

    return GCwithCov


def get_read_counts_table(path):
    """
    This method is only used to generate stats for un-collapsed bams
    """
    read_counts_path = '/'.join([path, WALTZ_READ_COUNTS_FILENAME])
    readCounts = pd.read_table(read_counts_path, index_col=0)

    readCounts = pd.melt(readCounts, id_vars=['ID'], var_name='Category')
    readCounts['Method'] = readCounts['Category'].apply(unique_or_tot)
    readCounts = readCounts.dropna(axis=0)
    readCounts['Category'] = readCounts['Category'].apply(rename_category)
    readCounts = readCounts.sort_values(['Method', 'Category'], ascending=False)
    readCounts = readCounts.reset_index(drop=True).rename(columns={'ID': 'Sample'})

    return readCounts


def get_coverage_table(path):
    tbl = pd.read_table('/'.join([path, WALTZ_COVERAGE_FILENAME]), header=0)
    coverage = pd.melt(tbl, id_vars='Sample', var_name='Method', value_name='AverageCoverage')
    coverage['Method'] = coverage['Method'].apply(unique_or_tot)

    return coverage


def get_collapsed_waltz_tables(path, method):
    '''
    Creates read_counts, coverage, and gc_bias tables for collapsed bam metrics.

    :param path:
    :param method:
    :return:
    '''
    read_counts_table = pd.read_table('/'.join([path, WALTZ_READ_COUNTS_FILENAME]), index_col=0)
    read_counts_table = pd.melt(read_counts_table, id_vars=['ID'], var_name='Category')
    read_counts_table['Category'] = read_counts_table['Category'].apply(rename_category_2)
    read_counts_table = read_counts_table.dropna(axis=0)
    read_counts_table['Method'] = [method.replace('Waltz', '')] * len(read_counts_table)
    read_counts_table = read_counts_table.rename(columns={'ID': 'Sample'})
    read_counts_table['value'] = read_counts_table['value'].astype(float)
    read_counts_table = read_counts_table.sort_values(['Method', 'Category'], ascending=False).reset_index(drop=True)

    coverage_table = pd.read_table('/'.join([path, WALTZ_COVERAGE_FILENAME]), usecols=[0, 1],
                                   names=['Sample', 'AverageCoverage'], header=0)
    coverage_table['Method'] = [method.replace('Waltz', '')] * len(coverage_table)

    gc_bias_table = get_gc_table(method, INTERVALS_FILENAME_SUFFIX, path)

    return [read_counts_table, coverage_table, gc_bias_table]


def get_tables_only_total(path):
    '''
    This table is used for:

      "Fraction of Total Reads that Align to the Human Genome" plot

    It looks like:

      Sample	                        TotalReads	UnmappedReads	TotalMapped	    DuplicateFraction	TotalOnTarget	TotalOnTargetFraction	AlignFrac	    TotalOffTargetFraction

      TD-191J-pl-UN-IGO-05500-EH-1	    109490111	210181	        109279930	    0.912883564256	    92437723	    0.85	                0.99808036545	0.15
      TD-191J-pl-K1-IGO-05500-EH-3	    115452783	218052	        115234731	    0.924371221034	    96750072	    0.84	                0.998111331799	0.16
      TD-191J-pl-K2-IGO-05500-EH-5	    112788589	174808	        112613781	    0.919883997146	    94166876	    0.84	                0.998450126901	0.16
      PR-brca-013-pl-UN-IGO-05500-EH-2	95797159	187660	        95609499	    0.911253117224	    75674559	    0.79	                0.998041069256	0.21
      PR-brca-013-pl-K1-IGO-05500-EH-4	94959861	191275	        94768586	    0.91845905562	    75317874	    0.79	                0.997985727886	0.21
      PR-brca-013-pl-K2-IGO-05500-EH-6	96176591	193777	        95982814	    0.923673231752	    76583786	    0.8	                    0.997985195795	0.2

    :param path:
    :return:
    '''
    readCountsTotal = pd.read_table('/'.join([path, WALTZ_READ_COUNTS_FILENAME]), index_col=0)

    col_idx = ~readCountsTotal.columns.str.contains('Unique')
    readCountsTotal = readCountsTotal.iloc[:, col_idx].rename(columns={'ID': 'Sample'})

    readCountsTotal['AlignFrac'] = readCountsTotal['TotalMapped'] / readCountsTotal['TotalReads']
    readCountsTotal['TotalOffTargetFraction'] = 1 - readCountsTotal['TotalOnTargetFraction']

    return readCountsTotal


def get_table_duplication(tbl):
    '''
    Creates duplication rate table

    This table looks like:

      DuplicationRate	Method	Sample

      0.912883564256	Picard	TD-191J-pl-UN-IGO-05500-EH-1
      0.924371221034	Picard	TD-191J-pl-K1-IGO-05500-EH-3
      0.919883997146	Picard	TD-191J-pl-K2-IGO-05500-EH-5
      0.911253117224	Picard	PR-brca-013-pl-UN-IGO-05500-EH-2
      0.91845905562	    Picard	PR-brca-013-pl-K1-IGO-05500-EH-4

    :param tbl:
    :return:
    '''
    mapped_idx = tbl['Category'].str.contains('Mapped')
    columns_idx = (mapped_idx & tbl['Method'].str.contains('Total'))
    mappedReadsTotal = tbl[columns_idx][['Sample', 'value']]
    methods = tbl['Method'].unique().tolist()

    methods.remove('Total')
    dupTable = pd.DataFrame(columns=DUPLICATION_RATES_HEADER)

    for method in methods:
        tbl_subset = tbl[mapped_idx & tbl['Method'].str.contains(method)]
        unique_counts = tbl_subset['value'].astype('float').values

        # Duplication rate = 1 - (unique mapped reads / total mapped reads)
        duplication_rate = np.subtract(1, np.divide(unique_counts, mappedReadsTotal['value'].values))

        newDf = pd.DataFrame({
            'Sample': mappedReadsTotal['Sample'].values,
            'Method': [method] * (len(mappedReadsTotal)),
            'DuplicationRate': duplication_rate
        })
        dupTable = pd.concat([dupTable, newDf])

    return dupTable


def get_gc_table_average_over_all_samples(tbl):
    '''
    Function to create GC content table: averaged over all samples

    This table looks like:

      Coverage	        GCbin	Method

      0.416920482145	0.15	Total
      0.649004746609	0.2	    Total
      ...
      0.438348274606	0.15	Picard
      0.652623804834	0.2	    Picard
      0.660778258693	0.25	Picard

    :param tbl:
    :return:
    '''
    final_bins_table = pd.DataFrame(columns=GC_BIAS_AVERAGE_COVERAGE_ALL_SAMPLES_HEADER)
    all_samples = tbl['Sample'].unique()
    all_methods = tbl['Method'].unique()

    minGC = np.min(tbl['GC'])
    maxGC = np.max(tbl['GC'])
    allBins = np.arange(round(minGC - np.mod(minGC, 0.05), 2), round(maxGC + 0.1 - np.mod(maxGC, 0.05), 2), 0.05)

    for method in all_methods:
        currTable = tbl[tbl['Method'] == method].copy()
        for sample in all_samples:
            currLoc = currTable['Sample'] == sample
            currAvg = np.mean(currTable.loc[currLoc, 'Coverage'])
            if (currAvg == 0):
                currTable.loc[currLoc, 'CoverageNorm'] = [0] * len(currTable.loc[currLoc, 'Coverage'].values)
            else:
                currTable.loc[currLoc, 'CoverageNorm'] = currTable.loc[currLoc, 'Coverage'].values / currAvg

        for bin in range(0, len(allBins) - 1):
            newDf = pd.DataFrame({
                'Method': [method],
                'GCbin': [allBins[bin]],
                'Coverage': [
                    np.mean(currTable[(currTable['GC'] >= allBins[bin]) & (currTable['GC'] < allBins[bin + 1])][
                                'CoverageNorm'])]
            })

            final_bins_table = pd.concat([final_bins_table, newDf])

    return final_bins_table


def get_gc_table_average_for_each_sample(tbl):
    '''
    Creates the GC content table, with each sample represented

    This table looks like:

      Coverage	        GCbin	Method	Sample

      0.742185452337	0.15	Total	PR-brca-013-pl-K1-IGO-05500-EH-4
      1.08003290945	    0.2	    Total	PR-brca-013-pl-K1-IGO-05500-EH-4
      0.955436250129	0.25	Total	PR-brca-013-pl-K1-IGO-05500-EH-4
      1.01493264757	    0.3	    Total	PR-brca-013-pl-K1-IGO-05500-EH-4
      1.03360931986	    0.35	Total	PR-brca-013-pl-K1-IGO-05500-EH-4
      1.02775119309	    0.4	    Total	PR-brca-013-pl-K1-IGO-05500-EH-4
      1.0051360653	    0.45	Total	PR-brca-013-pl-K1-IGO-05500-EH-4
      0.978072189524	0.5	    Total	PR-brca-013-pl-K1-IGO-05500-EH-4
      1.02552837954	    0.55	Total	PR-brca-013-pl-K1-IGO-05500-EH-4
      1.04039467378	    0.6	    Total	PR-brca-013-pl-K1-IGO-05500-EH-4

    :param tbl:
    :return:
    '''
    finalBinsTable = pd.DataFrame(columns=GC_BIAS_AVERAGE_COVERAGE_EACH_SAMPLE_HEADER)
    all_samples = tbl['Sample'].unique()
    all_methods = tbl['Method'].unique()
    minGC = np.min(tbl['GC'])
    maxGC = np.max(tbl['GC'])

    low_bin = round(minGC - np.mod(minGC, 0.05), 2)
    high_bin = round(maxGC + 0.1 - np.mod(maxGC, 0.05), 2)

    all_bins = np.arange(low_bin, high_bin, 0.05)

    for method in all_methods:
        for sample in all_samples:

            method_boolv = (tbl['Method'] == method)
            sample_boolv = (tbl['Sample'] == sample)

            currTable = tbl[method_boolv & sample_boolv].copy()
            currTable['CoverageNorm'] = currTable['Coverage'] / np.mean(currTable['Coverage'])

            for bin in range(0, len(all_bins) - 1):

                low_bin_boolv = (currTable['GC'] >= all_bins[bin])
                high_bin_boolv = (currTable['GC'] < all_bins[bin + 1])

                cur_gc_values = currTable[low_bin_boolv & high_bin_boolv]['CoverageNorm']
                avg_cov = np.mean(cur_gc_values)

                newDf = pd.DataFrame({
                    'Method': [method.replace('Waltz', '')],
                    'Sample': [sample],
                    'GCbin': [all_bins[bin]],
                    'Coverage': [avg_cov]
                })

                finalBinsTable = pd.concat([finalBinsTable, newDf])

    return finalBinsTable


def get_coverage_per_interval(tbl):
    '''
    Creates table of (un-collapsed) coverage per interval

    level_0	index	Coverage	Interval	    Sample	                        Gene	Probe
    0	    233	    27022.0	    exon_ALK_16.1_1	TD-191J-pl-K2-IGO-05500-EH-5	ALK	    16.1_1
    1	    243	    33926.0	    exon_ALK_23_1	TD-191J-pl-K2-IGO-05500-EH-5	ALK	    23_1
    2	    242	    25990.0	    exon_ALK_22.1_1	TD-191J-pl-K2-IGO-05500-EH-5	ALK	    22.1_1
    3	    241	    29409.0	    exon_ALK_21.1_1	TD-191J-pl-K2-IGO-05500-EH-5	ALK	    21.1_1

    :param tbl:
    :return:
    '''

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

    total_boolv = (tbl['Method'] == 'Total')
    # todo - why is this needed:
    exon_boolv = ['exon' in y for y in tbl['Interval']]
    finalTbl = tbl[total_boolv & exon_boolv][['Coverage', 'Interval', 'Sample']]
    # finalTbl = tbl[total_boolv][['Coverage', 'Interval', 'Sample']]

    gene_probe = [get_gene_and_probe(val) for val in finalTbl['Interval']]
    gene_probe_df = pd.DataFrame(gene_probe, columns=['Gene', 'Probe'])

    # todo: most likely, the reset_index() calls are unnecessary
    finalTbl = finalTbl.reset_index()
    finalTbl = pd.concat([finalTbl, gene_probe_df], axis=1)
    finalTbl = finalTbl.reset_index()

    return finalTbl


def get_insert_size_peaks_table(path):
    '''
    This table is used for the "Insert Size Distribution for All Samples" plot

    It looks like:

      PeakTotal	PeakTotalSize	PeakUnique	PeakUniqueSize	Sample

      1403704.0	165.0	70334.0	165.0	TD-191J-pl-UN-IGO-05500-EH-1
      1416357.0	165.0	63863.0	165.0	TD-191J-pl-K2-IGO-05500-EH-5
      648604.0	145.0	32919.0	145.0	PR-brca-013-pl-K2-IGO-05500-EH-6
      1478447.0	165.0	61024.0	165.0	TD-191J-pl-K1-IGO-05500-EH-3
      628741.0	165.0	38979.0	146.0	PR-brca-013-pl-UN-IGO-05500-EH-2
      624949.0	146.0	33673.0	146.0	PR-brca-013-pl-K1-IGO-05500-EH-4

    :param path: Path to Standard Waltz output Dir
    :return: pd.DataFrame of peaks
    '''
    files = [fileName for fileName in os.listdir(path) if FRAGMENT_SIZES_FILENAME_SUFFIX in fileName]

    finalTblPeaks = pd.DataFrame(columns=INSERT_SIZE_PEAKS_HEADER)
    for f in files:
        # Todo - part of my big sample name consistency problem
        sample = change_sample_name(f)

        cur_sizes = pd.read_csv(path + '/' + f, sep="\t", names=["Size", "PeakTotal", "PeakUnique"])
        max_tot = max(cur_sizes["PeakTotal"])
        max_unique = max(cur_sizes["PeakUnique"])
        max_tot_size = cur_sizes["Size"][np.argmax(cur_sizes["PeakTotal"])]
        max_unique_size = cur_sizes["Size"][np.argmax(cur_sizes["PeakUnique"])]

        finalTblPeaks = pd.concat([finalTblPeaks, pd.DataFrame({
            "Sample": sample,
            "PeakTotal": [max_tot],
            "PeakTotalSize": [max_tot_size],
            "PeakUnique": [max_unique],
            "PeakUniqueSize": [max_unique_size]
        })])

    return finalTblPeaks


def get_gc_coverage_table(std_waltz_path):
    total_gc_table = get_gc_table(TOTAL_LABEL, INTERVALS_FILENAME_SUFFIX, std_waltz_path)
    picard_gc_table = get_gc_table(PICARD_LABEL, INTERVALS_WITHOUT_DUPLICATES_FILENAME_SUFFIX, std_waltz_path)
    gc_cov_int_table = pd.concat([total_gc_table, picard_gc_table])
    gc_cov_int_table = gc_cov_int_table.sort_values(['Method'], ascending=False)
    return gc_cov_int_table


########
# Main #
########

def main(args):
    output_dir = args.tables_output_dir
    std_waltz_path = args.standard_waltz_dir

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Output file names
    READ_COUNTS_FILENAME = '/'.join([output_dir, 'read-counts-agg.txt'])
    COVERAGE_AGG_FILENAME = '/'.join([output_dir, 'coverage-agg.txt'])
    ALL_SAMPLES_COVERAGE_FILENAME = '/'.join([output_dir, 'GC-bias-with-coverage-averages-over-all-samples.txt'])
    EACH_SAMPLE_COVERAGE_FILENAME = '/'.join([output_dir, 'GC-bias-with-coverage-averages-over-each-sample.txt'])
    GC_BIAS_WITH_COVERAGE_FILENAME = '/'.join([output_dir, 'GC-bias-with-coverage.txt'])
    INSERT_SIZE_PEAKS_FILENAME = '/'.join([output_dir, 'insert-size-peaks.txt'])
    READ_COUNTS_TOTAL_FILENAME = '/'.join([output_dir, 'read-counts-total.txt'])
    COVERAGE_PER_INTERVAL_FILENAME = '/'.join([output_dir, 'coverage-per-interval.txt'])
    DUPLICATION_RATES_FILENAME = '/'.join([output_dir, 'duplication-rates.txt'])

    # Get our 5 base tables
    read_counts_table = get_read_counts_table(std_waltz_path)
    coverage_table = get_coverage_table(std_waltz_path)
    gc_cov_int_table = get_gc_coverage_table(std_waltz_path)
    insert_size_peaks_table = get_insert_size_peaks_table(std_waltz_path)
    read_counts_total_table = get_tables_only_total(std_waltz_path)

    # Add in the Marianas Unfiltered tables
    if hasattr(args, 'marianas_unfiltered_waltz_dir') and args.marianas_unfiltered_waltz_dir is not None:
        mw = get_collapsed_waltz_tables(args.marianas_unfiltered_waltz_dir, MARIANAS_UNFILTERED_WALTZ_COLLAPSING_METHOD)
        read_counts_table = pd.concat([read_counts_table, mw[0]])
        coverage_table = pd.concat([coverage_table, mw[1]])
        gc_cov_int_table = pd.concat([gc_cov_int_table, mw[2]])

    # Add in the Marianas Simplex Duplex tables
    if hasattr(args, 'marianas_simplex_duplex_waltz_dir') and args.marianas_simplex_duplex_waltz_dir is not None:
        mw = get_collapsed_waltz_tables(args.marianas_simplex_duplex_waltz_dir, MARIANAS_SIMPLEX_DUPLEX_WALTZ_COLLAPSING_METHOD)
        read_counts_table = pd.concat([read_counts_table, mw[0]])
        coverage_table = pd.concat([coverage_table, mw[1]])
        gc_cov_int_table = pd.concat([gc_cov_int_table, mw[2]])

    # Add in the Marianas Duplex tables
    if hasattr(args, 'marianas_duplex_waltz_dir') and args.marianas_duplex_waltz_dir is not None:
        mw = get_collapsed_waltz_tables(args.marianas_duplex_waltz_dir, MARIANAS_DUPLEX_WALTZ_COLLAPSING_METHOD)
        read_counts_table = pd.concat([read_counts_table, mw[0]])
        coverage_table = pd.concat([coverage_table, mw[1]])
        gc_cov_int_table = pd.concat([gc_cov_int_table, mw[2]])

    # Fix sample names
    tables = [read_counts_table, coverage_table, gc_cov_int_table, insert_size_peaks_table, read_counts_total_table]
    tables = [fix_sample_names(tbl) for tbl in tables]
    read_counts_table, coverage_table, gc_cov_int_table, insert_size_peaks_table, read_counts_total_table = tables

    # Use base tables for additional tables
    gc_avg_table_all = get_gc_table_average_over_all_samples(gc_cov_int_table)
    gc_avg_table_each = get_gc_table_average_for_each_sample(gc_cov_int_table)
    coverage_per_interval_table = get_coverage_per_interval(gc_cov_int_table)
    duplication_table = get_table_duplication(read_counts_table)

    # Write all tables
    read_counts_table.to_csv(READ_COUNTS_FILENAME, sep='\t', index=False)
    read_counts_total_table.to_csv(READ_COUNTS_TOTAL_FILENAME, sep='\t', index=False)
    coverage_table.to_csv(COVERAGE_AGG_FILENAME, sep='\t', index=False)
    insert_size_peaks_table.to_csv(INSERT_SIZE_PEAKS_FILENAME, sep='\t', index=False)
    gc_cov_int_table.to_csv(GC_BIAS_WITH_COVERAGE_FILENAME, sep='\t', index=False)
    gc_avg_table_each.to_csv(EACH_SAMPLE_COVERAGE_FILENAME, sep='\t', index=False)
    gc_avg_table_all.to_csv(ALL_SAMPLES_COVERAGE_FILENAME, sep='\t', index=False)
    coverage_per_interval_table.to_csv(COVERAGE_PER_INTERVAL_FILENAME, sep='\t', index=False)
    duplication_table.to_csv(DUPLICATION_RATES_FILENAME, sep='\t', index=False)
