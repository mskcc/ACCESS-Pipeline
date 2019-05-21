import os
import unittest
import pandas as pd

from pandas.util.testing import assert_frame_equal

from python_tools.util import ArgparseMock
from python_tools.workflow_tools.qc import tables_module
from python_tools.constants import ALL_TABLES_MODULE_OUTPUT_FILES



class TablesModuleTest(unittest.TestCase):

    def setUp(self):
        """
        Creates mock argparse args (paths to waltz test data)

        :return:
        """
        # Allow us to use paths relative to the current directory's tests
        os.chdir('test__tables_module')

        self.tables_module_params = {
            'standard_waltz_pool_a':        './test_data/waltz_standard_pool_a',
            'unfiltered_waltz_pool_a':      './test_data/waltz_unfiltered_pool_a',
            'simplex_waltz_pool_a':         './test_data/waltz_simplex_pool_a',
            'duplex_waltz_pool_a':          './test_data/waltz_duplex_pool_a',
            'standard_waltz_pool_b':        './test_data/waltz_standard_pool_b',
            'unfiltered_waltz_pool_b':      './test_data/waltz_unfiltered_pool_b',
            'simplex_waltz_pool_b':         './test_data/waltz_simplex_pool_b',
            'duplex_waltz_pool_b':          './test_data/waltz_duplex_pool_b',

            'standard_waltz_metrics_pool_a_exon_level':        './test_data/waltz_standard_a_exon_level_files',
            'unfiltered_waltz_metrics_pool_a_exon_level':      './test_data/waltz_unfiltered_a_exon_level_files',
            'simplex_waltz_metrics_pool_a_exon_level':         './test_data/waltz_simplex_a_exon_level_files',
            'duplex_waltz_metrics_pool_a_exon_level':          './test_data/waltz_duplex_a_exon_level_files',
        }

    def tearDown(self):
        """
        Deletes output files

        :return:
        """
        for f in ALL_TABLES_MODULE_OUTPUT_FILES:
            os.unlink(f)

        # Move back up to main test dir
        os.chdir('..')

    def test_tables_module(self):
        """
        Test that the tables module runs without error

        :return:
        """
        argparse_mock = ArgparseMock(self.tables_module_params)
        tables_module.create_combined_qc_tables(argparse_mock)

        for output_file in ALL_TABLES_MODULE_OUTPUT_FILES:
            print(output_file)
            actual = pd.read_csv(output_file, sep='\t')
            expected = pd.read_csv('expected_output/' + output_file, sep='\t')
            assert_frame_equal(actual, expected)


if __name__ == '__main__':
    unittest.main()
