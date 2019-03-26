import os
import unittest

from constants import ALL_TABLES_MODULE_OUTPUT_FILES
from python_tools.workflow_tools.qc import tables_module


class ArgparseMock():
    """
    Mock class to simply have keys and values that simulate the argparse object that the tables module uses
    """
    def __init__(self, args):

        for key, value in zip(args.keys(), args.values()):

            setattr(self, key, value)


class TablesModuleTest(unittest.TestCase):

    def setUp(self):
        """
        Creates mock argparse args (paths to waltz test data)

        :return:
        """
        self.tables_module_params = {
            'standard_waltz_pool_a':        './test_data/test_waltz_output/waltz_standard_pool_a',
            'unfiltered_waltz_pool_a':      './test_data/test_waltz_output/waltz_unfiltered_pool_a',
            'simplex_waltz_pool_a':         './test_data/test_waltz_output/waltz_simplex_pool_a',
            'duplex_waltz_pool_a':          './test_data/test_waltz_output/waltz_duplex_pool_a',
            'standard_waltz_pool_b':        './test_data/test_waltz_output/waltz_standard_pool_b',
            'unfiltered_waltz_pool_b':      './test_data/test_waltz_output/waltz_unfiltered_pool_b',
            'simplex_waltz_pool_b':         './test_data/test_waltz_output/waltz_simplex_pool_b',
            'duplex_waltz_pool_b':          './test_data/test_waltz_output/waltz_duplex_pool_b',

            'standard_waltz_metrics_pool_a_exon_level':        './test_data/test_waltz_output/waltz_standard_pool_a_exon_level',
            'unfiltered_waltz_metrics_pool_a_exon_level':      './test_data/test_waltz_output/waltz_unfiltered_pool_a_exon_level',
            'simplex_waltz_metrics_pool_a_exon_level':         './test_data/test_waltz_output/waltz_simplex_pool_a_exon_level',
            'duplex_waltz_metrics_pool_a_exon_level':          './test_data/test_waltz_output/waltz_duplex_pool_a_exon_level',
        }

    def tearDown(self):
        """
        Deletes output files

        :return:
        """
        for f in ALL_TABLES_MODULE_OUTPUT_FILES:
            os.unlink(f)

        os.unlink('./fragment-sizes.txt')

    def test_tables_module(self):
        """
        Test that the tables module runs without error

        :return:
        """
        argparse_mock = ArgparseMock(self.tables_module_params)
        tables_module.create_combined_qc_tables(argparse_mock)


if __name__ == '__main__':
    unittest.main()
