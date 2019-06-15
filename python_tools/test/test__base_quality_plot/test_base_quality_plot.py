import os
import shutil
import unittest
import pandas as pd

from python_tools.workflow_tools.qc.base_quality_plot import (
    read_quality_tables,
    base_quality_plot
)


class BaseQualityPlotsTestCase(unittest.TestCase):

    def setUp(self):
        """
        Set some constants used for testing

        :return:
        """
        # Allow us to use paths relative to the current directory's tests
        # os.chdir('test__base_quality_plot')

        # Set up test outputs directory
        os.mkdir('./test_output')

        self.picard_metrics_directory = './test_data'

    def tearDown(self):
        """
        Remove test outputs after each test

        :return:
        """
        shutil.rmtree('./test_output')

        # Move back up to main test dir
        os.chdir('..')

    # @image_comparison(baseline_images=['base_quality_plot.pdf'], extensions=['png'])
    def test_base_quality_plot(self):
        quality_table = read_quality_tables(self.picard_metrics_directory).fillna(0)
        base_quality_plot(quality_table)

        # result = pd.read_csv('base_quality_table.tsv', sep='\t')
        # expected_result = pd.read_csv('expected_results/base_quality_table.tsv', sep='\t')
        # assert result.equals(expected_result)
        assert os.path.exists('base_quality_plot.pdf')


if __name__ == '__main__':
    unittest.main()
