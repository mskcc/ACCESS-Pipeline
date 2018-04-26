#######################################################
# Innovation-QC Module
# Innovation Laboratory
# Center For Molecular Oncology
# Memorial Sloan Kettering Cancer Research Center
# maintainer: Ian Johnson (johnsoni@mskcc.org)
#######################################################

'''
This module will group Samples per Lane #, and run the table-generation module
and plot-generation module once per Lane.
'''

import os
import re
import pandas as pd
import argparse
import subprocess

import qc


BASE = os.getcwd() + '/'


def run_table_module(folders, tables_output_dir):
    '''
    Run the table submodule
    :param folders:
    :param tables_output_dir:
    :return:
    '''
    # Todo: mocking argparse object, not clean
    class Args():
        def __init__(self):
            self.data = {}
        def __setitem__(self, key, value):
            self.data[key] = value

    args = Args()

    setattr(args, 'tables_output_dir', tables_output_dir)

    for prefix, _, new_dir in folders:
        setattr(args, prefix, BASE + new_dir)

    qc.main(args)


def run_plots_module(standard_waltz_dir, tables_output_dir, plots_output_dir, title_file_path):
    '''
    Run the plots submodule
    :param standard_waltz_dir:
    :param tables_output_dir:
    :param plots_output_dir:
    :param title_file:
    :return:
    '''
    # Note: The following script should be found in your Virtual
    # environment PATH (/somewhere/virtualenv/bin/plotting-collapsed-bams.r)
    # after installing this module with `python setup.py install`
    plots_module_cmd = 'plotting-collapsed-bams.r'

    plots_module_cmd += ' -i {} -w {} -o {}'.format(tables_output_dir, standard_waltz_dir, plots_output_dir)
    plots_module_cmd += ' -t {}'.format(title_file_path)

    print('Running plots module with cmd: {}'.format(plots_module_cmd))
    rv = subprocess.check_call(plots_module_cmd, shell=True)
    print("Plots module return code: " + str(rv))

    # Raise error to prevent Toil job from finishing successfully
    if rv != 0:
        raise Exception('Plots module failed')


def cleanup_sample_names(tbl):
    if 'Sample' in tbl.columns:
        tbl['Sample'].replace(to_replace='_.\d\d\.bam', value='', inplace=True, regex=True)
        tbl['Sample'].replace(to_replace='_.\d\d$', value='', inplace=True, regex=True)
        tbl['Sample'] = tbl['Sample'].str.replace('FulcrumCollapsed_', '')
        tbl['Sample'] = tbl['Sample'].str.replace('Sample_', '')
        tbl['Sample'] = tbl['Sample'].str.replace('\.bam.*', '')
        tbl['Sample'] = tbl['Sample'].str.replace('.bam', '')
        tbl['Sample'] = tbl['Sample'].str.replace('_md', '')
    else:
        tbl['ID'].replace(to_replace='_.\d\d\.bam', value='', inplace=True, regex=True)
        tbl['ID'].replace(to_replace='_.\d\d$', value='', inplace=True, regex=True)
        tbl['ID'] = tbl['ID'].str.replace('FulcrumCollapsed_', '')
        tbl['ID'] = tbl['ID'].str.replace('Sample_', '')
        tbl['ID'] = tbl['ID'].str.replace('\.bam.*', '')
        tbl['ID'] = tbl['ID'].str.replace('.bam', '')
        tbl['ID'] = tbl['ID'].str.replace('_md', '')
    return tbl


def run_table_module_for_group(sample_group, folder_pairs, tables_output_dir):
    '''
    This method takes care of copying various Waltz output files in preparation for running the table_module
    :param sample_group: List of Sample_ID's for current QC group
    :param folder_pairs: List of tuples (Waltz_output_dir, New_dir_to_copy_to, folder_type_string_abbreviation)
    :param tables_output_dir: String of folder to save results to
    :return:
    '''
    print("Sample Group: ", sample_group)

    for _, waltz_output_dir, new_dir in folder_pairs:
        waltz_output_files = os.listdir(waltz_output_dir)

        # Filter down to just files that we're interested in for this group of samples
        group_files = filter(lambda x: any([sample in x for sample in sample_group]), waltz_output_files)

        print("Sample Group: ", sample_group)
        print("Group files: ")
        print(group_files)

        # Copy them to our target directory
        for src in group_files:
            target = new_dir + '/' + src
            os.symlink(waltz_output_dir + '/' + src, target)

        # Also copy the three aggregated metrics files,
        # but filter down to just samples we're interested in
        sample_search = '|'.join(sample_group)

        read_counts = pd.read_csv(waltz_output_dir + '/read-counts.txt', sep='\t')
        read_counts = cleanup_sample_names(read_counts)
        boolv = read_counts['ID'].astype(object).str.contains(sample_search, na=False)
        read_counts_sub = read_counts[boolv]
        read_counts_sub.to_csv(new_dir + '/read-counts.txt', sep='\t', index=False)

        waltz_coverage = pd.read_csv(waltz_output_dir + '/waltz-coverage.txt', sep='\t')
        waltz_coverage = cleanup_sample_names(waltz_coverage)
        boolv = waltz_coverage['Sample'].astype(object).str.contains(sample_search, na=False)
        waltz_coverage_sub = waltz_coverage[boolv]
        waltz_coverage_sub.to_csv(new_dir + '/waltz-coverage.txt', sep='\t', index=False)

        fragment_sizes = pd.read_csv(waltz_output_dir + '/fragment-sizes.txt', sep='\t')
        fragment_sizes = cleanup_sample_names(fragment_sizes)
        boolv = fragment_sizes['Sample'].astype(object).str.contains(sample_search, na=False)
        fragment_sizes_sub = fragment_sizes[boolv]
        fragment_sizes_sub.to_csv(new_dir + '/fragment-sizes.txt', sep='\t', index=False)

    run_table_module(folder_pairs, tables_output_dir)


def generate_sample_id_variations(groups):
    '''
    Util method to cover all our bases when some sample IDs have inconsistent use of dashes vs underscores
    Also tries sample names with '.bam' file extension removed
    :param groups:
    :return:
    '''
    # Matches "_S41" at end of string:
    suffix_regex = re.compile(r'_.\d\d\.bam')

    # Copy the original groups
    new_groups = groups[:]
    for group in groups:
        if '-' in group:
            new_group = group.replace('-', '_')
            new_groups.append(new_group)
        if '_'in group:
            new_group = group.replace('_', '-')
            new_groups.append(new_group)
        if '.bam' in group:
            new_group = group.replace('.bam', '')
            new_groups.append(new_group)
        if '_md' in group:
            new_group = group.replace('_md', '')
            new_groups.append(new_group)
        if '_md.bam' in group:
            new_group = group.replace('_md.bam', '')
            new_groups.append(new_group)
        if 'Sample_' in group:
            new_group = group.replace('Sample_', '')
            new_groups.append(new_group)
        if suffix_regex.match(group):
            new_group = re.sub(suffix_regex, '.bam', group)
            new_groups.append(new_group)

    return new_groups


def run_qc_for_lanes(args):
    '''
    Parse command line arguments, create sample groups, make directory structure, run submodules.
    Called by if __name__ == __main__
    :return:
    '''
    standard_waltz_dir = args.standard_waltz_dir
    marianas_unfiltered_waltz_dir = args.marianas_unfiltered_waltz_dir
    marianas_simplex_duplex_waltz_dir = args.marianas_simplex_duplex_waltz_dir
    marianas_duplex_waltz_dir = args.marianas_duplex_waltz_dir

    # Read in the Title File
    title_file_path = args.title_file_path
    title_file = pd.read_csv(title_file_path, sep='\t')

    # QC module will be run for each Lane
    for lane in title_file['Lane'].unique():
        title_file_sub = title_file[title_file['Lane'] == lane]
        title_file_sub_path = './title_file_sub.txt'
        title_file_sub.to_csv(title_file_sub_path, sep='\t', index=False)

        if 'Sample_ID' in title_file_sub.columns.tolist():
            sample_group = title_file_sub['Sample_ID'].tolist()
        elif 'SampleID' in title_file_sub.columns.tolist():
            sample_group = title_file_sub['SampleID'].tolist()
        else:
            raise Exception('Title File should have a Sample ID column')

        # Here we use our sample names utility method to search for possible
        # alternative sample names. The reason we call it twice is to generate
        # combinations of 2 modifications to the sample name
        # Ex: Sample_xxxx_xxxx_.bam --> xxxx_xxxx (removes "Sample_" and ".bam")
        sample_group = generate_sample_id_variations(sample_group)
        sample_group = generate_sample_id_variations(sample_group)
        # Remove duplicates
        sample_group = list(set(sample_group))

        RESULTS_DIR = 'results/lane-{}/'.format(lane)

        plots_output_dir = RESULTS_DIR + 'final-plots'
        os.makedirs(plots_output_dir)

        sw = RESULTS_DIR + 'standard-waltz-output'
        tables_output_dir = RESULTS_DIR + 'tables-output'
        os.makedirs(sw)
        os.makedirs(tables_output_dir)

        folder_pairs = [('standard_waltz_dir', standard_waltz_dir, sw)]

        # We will run the QC for each subset of samples (each group)
        if marianas_unfiltered_waltz_dir:
            mu = RESULTS_DIR + 'marianas_unfiltered-waltz-output'
            os.makedirs(mu)
            folder_pairs += [('marianas_unfiltered_waltz_dir', marianas_unfiltered_waltz_dir, mu)]
        if marianas_simplex_duplex_waltz_dir:
            ms = RESULTS_DIR + 'marianas_simplex_duplex-waltz-output'
            os.makedirs(ms)
            folder_pairs += [('marianas_simplex_duplex_waltz_dir', marianas_simplex_duplex_waltz_dir, ms)]
        if marianas_duplex_waltz_dir:
            md = RESULTS_DIR + 'marianas_duplex-waltz-output'
            os.makedirs(md)
            folder_pairs += [('marianas_duplex_waltz_dir', marianas_duplex_waltz_dir, md)]

        run_table_module_for_group(sample_group, folder_pairs, tables_output_dir)

        run_plots_module(BASE + sw, tables_output_dir, plots_output_dir, title_file_path=title_file_sub_path)


class FullPaths(argparse.Action):
    '''
    Expand user- and relative-paths
    '''
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


def main():
    print "Working Dir: " + os.getcwd()

    parser = argparse.ArgumentParser(description='Innovation QC module', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-t', '--title_file_path', type=str, default=None, required=True, action=FullPaths)
    parser.add_argument('-sw', '--standard_waltz_dir', type=str, default=None, required=True, action=FullPaths)
    parser.add_argument('-mu', '--marianas_unfiltered_waltz_dir', type=str, default=None, action=FullPaths)
    parser.add_argument('-ms', '--marianas_simplex_duplex_waltz_dir', type=str, default=None, action=FullPaths)
    parser.add_argument('-md', '--marianas_duplex_waltz_dir', type=str, default=None, action=FullPaths)
    args = parser.parse_args()

    run_qc_for_lanes(args)


if __name__ == '__main__':
    main()
