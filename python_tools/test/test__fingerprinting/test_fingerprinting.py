import os
import shutil
import unittest
import pandas as pd

from python_tools.workflow_tools.qc.fingerprinting import (
    read_csv,
    plot_genotyping_matrix
)


class FingerprintingTestCase(unittest.TestCase):

    def setUp(self):
        """
        Set some constants used for testing

        :return:
        """
        # CD into this test module if running all tests together
        if os.path.isdir('test__fingerprinting'):
            os.chdir('test__fingerprinting')

        # Set up test outputs directory
        os.mkdir('./test_output')

    def tearDown(self):
        """
        Remove test outputs after each test

        :return:
        """
        shutil.rmtree('./test_output')

        # Move back up to main test dir
        os.chdir('..')

    def test_plot_genotpying_matrix(self):
        geno_compare = read_csv('./test_data/Geno_compare.txt')
        title_file = pd.read_csv('./test_data/title_file.txt')
        plot_genotyping_matrix(geno_compare, './test_output/', title_file)

if __name__ == '__main__':
    unittest.main()
