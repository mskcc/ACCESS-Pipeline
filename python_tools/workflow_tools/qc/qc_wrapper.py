##################################################
# ACCESS QC Module
# Innovation Laboratory
# Center For Molecular Oncology
# Memorial Sloan Kettering Cancer Research Center
# maintainer: Ian Johnson (johnsoni@mskcc.org)
##################################################


import logging
import argparse
import subprocess

import tables_module
from ...constants import *


PLOTS_MODULE_BASE = 'plots_module.r'


def run_plots_module(tables_output_dir, plots_output_dir, title_file_path, inputs_yaml_path):
    """
    Note: The R script should be found in your Virtual
    environment PATH (/somewhere/virtualenv/bin/plots_module.r)
    after installing with `python setup.py install`
    """
    plots_module_cmd = PLOTS_MODULE_BASE
    plots_module_cmd += ' -i {} '.format(tables_output_dir)
    plots_module_cmd += ' -o {} '.format(plots_output_dir)
    plots_module_cmd += ' -t {} '.format(title_file_path)
    plots_module_cmd += ' -y {} '.format(inputs_yaml_path)

    logging.info('Running plots module with cmd: {}'.format(plots_module_cmd))
    rv = subprocess.check_call(plots_module_cmd, shell=True)
    logging.info("Plots module return code: " + str(rv))

    # Raise error to prevent Toil job from finishing successfully
    if rv != 0:
        raise Exception('Plots module failed')


class FullPaths(argparse.Action):
    """
    Expand user and relative-paths
    """
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))


def main():
    parser = argparse.ArgumentParser(description='MSK ACCESS QC module', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-t', '--title_file_path', type=str, default=None, required=True, action=FullPaths)
    parser.add_argument('-y', '--inputs_yaml_path', type=str, default=None, required=True, action=FullPaths)
    parser.add_argument('-swa', '--standard_waltz_pool_a', type=str, default=None, required=True, action=FullPaths)
    parser.add_argument('-mua', '--unfiltered_waltz_pool_a', type=str, default=None, action=FullPaths)
    parser.add_argument('-msa', '--simplex_waltz_pool_a', type=str, default=None, action=FullPaths)
    parser.add_argument('-mda', '--duplex_waltz_pool_a', type=str, default=None, action=FullPaths)

    parser.add_argument('-swb', '--standard_waltz_pool_b', type=str, default=None, required=True, action=FullPaths)
    parser.add_argument('-mub', '--unfiltered_waltz_pool_b', type=str, default=None, action=FullPaths)
    parser.add_argument('-msb', '--simplex_waltz_pool_b', type=str, default=None, action=FullPaths)
    parser.add_argument('-mdb', '--duplex_waltz_pool_b', type=str, default=None, action=FullPaths)
    args = parser.parse_args()

    RESULTS_BASE = os.path.join(os.getcwd(), 'results')
    plots_output_dir = os.path.join(RESULTS_BASE, 'final_plots')
    tables_output_dir = os.path.join(RESULTS_BASE, 'tables_output')
    setattr(args, 'tables_output_dir', tables_output_dir)

    # Run tables module
    tables_module.main(args)

    # Run plots module
    run_plots_module(tables_output_dir, plots_output_dir, args.title_file_path, args.inputs_yaml_path)
