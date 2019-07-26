import os
import shutil
import unittest
import pandas as pd

from python_tools.workflow_tools.qc.plot_noise import (
    noise_contributing_sites_plot,
    noise_alt_percent_plot,
    noise_by_substitution_plot
)


class NoisePlotsTestCase(unittest.TestCase):

    def setUp(self):
        """
        Set some constants used for testing

        :return:
        """
        # CD into this test module if running all tests together
        if os.path.isdir('test__noise_plots'):
            os.chdir('test__noise_plots')

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

    def load_good_title_file(self):
        title_file = pd.read_csv('../test_data/good_title_file.txt', sep='\t')
        return title_file

    def load_noise_table(self):
        noise_table = pd.read_csv('noise/noise.txt', sep='\t')
        return noise_table

    def load_noise_by_substitution_table(self):
        noise_table = pd.read_csv('noise/noise-by-substitution.txt', sep='\t')
        return noise_table

    def load_noise_by_substitution_table_2(self):
        noise_table = pd.read_csv('noise/noise-by-substitution_2.txt', sep='\t')
        return noise_table

    # Todo: Use png's and figure out why this decorator doesn't call our test function
    # @image_comparison(baseline_images=['alt_percent_plot'], extensions=['pdf'])
    def test_alt_percent_plot(self):
        noise_table = self.load_noise_table()
        noise_alt_percent_plot(noise_table)
        assert os.path.exists('NoiseAltPercent.pdf')
        os.unlink('./NoiseAltPercent.pdf')

    # @image_comparison(baseline_images=['NoiseContributingSites'], extensions=['png'])
    def test_contributing_sites_plot(self):
        noise_table = self.load_noise_table()
        noise_contributing_sites_plot(noise_table)
        assert os.path.exists('NoiseContributingSites.pdf')
        os.unlink('./NoiseContributingSites.pdf')

    @unittest.skipIf('TRAVIS' in os.environ and os.environ['TRAVIS'] == 'true', 'Skipping this test on Travis CI.')
    # @image_comparison(baseline_images=['NoiseContributingSites'], extensions=['png'])
    def test_noise_by_substitution_plot(self):
        noise_table = self.load_noise_by_substitution_table()
        noise_by_substitution_plot(noise_table)
        result = pd.read_csv('noise_by_substitution.tsv', sep='\t')
        expected_result = pd.read_csv('expected_results/noise_by_substitution.tsv', sep='\t')
        assert result.equals(expected_result)
        assert os.path.exists('noise_by_substitution.pdf')
        os.unlink('./noise_by_substitution.pdf')

    @unittest.skipIf('TRAVIS' in os.environ and os.environ['TRAVIS'] == 'true', 'Skipping this test on Travis CI.')
    # @image_comparison(baseline_images=['NoiseContributingSites'], extensions=['png'])
    def test_noise_by_substitution_plot_2(self):
        noise_table = self.load_noise_by_substitution_table_2()
        noise_by_substitution_plot(noise_table)
        assert os.path.exists('noise_by_substitution.pdf')
        os.unlink('./noise_by_substitution.pdf')



if __name__ == '__main__':
    unittest.main()
