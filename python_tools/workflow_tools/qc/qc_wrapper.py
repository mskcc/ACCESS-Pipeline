#######################################################
# Innovation-QC Module
# Innovation Laboratory
# Center For Molecular Oncology
# Memorial Sloan Kettering Cancer Research Center
# maintainer: Ian Johnson (johnsoni@mskcc.org)
#######################################################


# This module will group Samples per Lane #, and run the table-generation module
# and plot-generation module once per Lane.


import argparse
import subprocess
import pandas as pd

import qc
from ...constants import *


BASE = os.getcwd() + '/'
RESULTS_BASE = 'results'


def run_table_module(folders, tables_output_dir):
    """
    Run the table submodule
    """
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
    """
    Run the plots submodule
    """
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


def cleanup_sample_names(table, sample_names):
    """
    Title File      Waltz Output
    Sample_ID       Sample
    asdf_123        asdf_123_MD_IR_FX_BR

    -->

    Sample_ID       Sample
    asdf_123        asdf_123
    """
    sample_id_search = r'|'.join(sample_names)
    sample_id_search = r'.*(' + sample_id_search + ').*'
    replaced = table[SAMPLE_ID_COLUMN].str.replace(sample_id_search, r'\1')
    table[SAMPLE_ID_COLUMN] = replaced
    return table


def subset_and_save_file(filename, sample_names, waltz_src, waltz_dst):
    """
    Subset data file `filename` to only samples in `sample_names`
    """
    file_path = os.path.join(waltz_src, filename)
    file_path_dst = os.path.join(waltz_dst, filename)

    sample_search = '|'.join(sample_names)

    df = pd.read_csv(file_path, sep='\t')
    # df = cleanup_sample_names(df, sample_names)
    boolv = df[SAMPLE_ID_COLUMN].astype(object).str.contains(sample_search, na=False)
    read_counts_sub = df[boolv]

    read_counts_sub.to_csv(file_path_dst, sep='\t', index=False)


def run_table_module_for_group(sample_group, folder_pairs, tables_output_dir):
    """
    This method takes care of copying and subsetting various Waltz output files,
    in preparation for running the table_module and plots_module

    :param sample_group: List of Sample_ID's for current QC group
    :param folder_pairs: List of tuples (Waltz_output_dir, New_dir_to_copy_to, folder_type_string_abbreviation)
    :param tables_output_dir: String of folder to save results to
    """
    for _, waltz_src, waltz_dst in folder_pairs:
        waltz_output_files = os.listdir(waltz_src)

        # Filter down to just files that we're interested in for this group of samples
        group_files = filter(lambda x: any([sample in x for sample in sample_group]), waltz_output_files)

        # Copy them to our target directory
        for src in group_files:
            target = waltz_dst + '/' + src
            os.symlink(waltz_src + '/' + src, target)

        # Also copy the three aggregated metrics files,
        # but filter down to just samples we're interested in
        subset_and_save_file('read-counts.txt', sample_group, waltz_src, waltz_dst)
        subset_and_save_file('waltz-coverage.txt', sample_group, waltz_src, waltz_dst)
        subset_and_save_file('fragment-sizes.txt', sample_group, waltz_src, waltz_dst)

    run_table_module(folder_pairs, tables_output_dir)


def run_qc_for_lane(title_file, lane, args):
    standard_waltz_dir = args.standard_waltz_dir
    marianas_unfiltered_waltz_dir = args.marianas_unfiltered_waltz_dir
    marianas_simplex_duplex_waltz_dir = args.marianas_simplex_duplex_waltz_dir
    marianas_duplex_waltz_dir = args.marianas_duplex_waltz_dir

    # Write the new title file for just this lane
    title_file_sub = title_file[title_file['Lane'] == lane]
    title_file_sub_path = './title_file_lane-{}.txt'.format(lane)
    title_file_sub.to_csv(title_file_sub_path, sep='\t', index=False)

    sample_group = title_file_sub[TITLE_FILE__SAMPLE_ID_COLUMN].tolist()

    RESULTS_DIR = os.path.join(RESULTS_BASE, 'lane-{}'.format(lane))

    plots_output_dir = os.path.join(RESULTS_DIR, 'final_plots')
    tables_output_dir = os.path.join(RESULTS_DIR, 'tables_output')
    os.makedirs(plots_output_dir)
    os.makedirs(tables_output_dir)

    folder_pairs = [
        ('standard_waltz', standard_waltz_dir),
        ('marianas_unfiltered_waltz', marianas_unfiltered_waltz_dir),
        ('marianas_simplex_duplex_waltz', marianas_simplex_duplex_waltz_dir),
        ('marianas_duplex_waltz', marianas_duplex_waltz_dir)
    ]

    folder_pairs_with_results_folder = []
    for waltz_src_name, waltz_src_loc in folder_pairs:
        waltz_dst = os.path.join(RESULTS_DIR, waltz_src_name)
        os.makedirs(waltz_dst)
        folder_pairs_with_results_folder += [(waltz_src_name, waltz_src_loc, waltz_dst)]

    run_table_module_for_group(sample_group, folder_pairs_with_results_folder, tables_output_dir)

    # Todo: same folder is referenced twice:
    std_waltz_loc = os.path.join(*[BASE, RESULTS_DIR, 'standard_waltz'])
    run_plots_module(std_waltz_loc, tables_output_dir, plots_output_dir, title_file_path=title_file_sub_path)


def run_qc_for_lanes(args):
    """
    Run QC tables and plots generation on a lane by lane basis
    """
    title_file_path = args.title_file_path
    title_file = pd.read_csv(title_file_path, sep='\t')

    for lane in title_file['Lane'].unique():
        run_qc_for_lane(title_file, lane, args)


class FullPaths(argparse.Action):
    """
    Expand user and relative-paths
    """
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
