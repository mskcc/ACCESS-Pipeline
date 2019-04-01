import os
import unittest
import pandas as pd

from python_tools.workflow_tools.qc.plot_noise import (
    noise_contributing_sites_plot,
    noise_alt_percent_plot,
    noise_by_substitution_plot
)


class NoisePlotsTestCase(unittest.TestCase):

    def load_good_title_file(self):
        title_file = pd.read_csv('test_data/good_title_file.txt', sep='\t')
        return title_file

    def load_noise_table(self):
        noise_table = pd.read_csv('test_data/noise/noise.txt', sep='\t')
        return noise_table

    def load_noise_by_substitution_table(self):
        noise_table = pd.read_csv('test_data/noise/noise-by-substitution.txt', sep='\t')
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

    # @image_comparison(baseline_images=['NoiseContributingSites'], extensions=['png'])
    def test_noise_by_substitution_plot(self):
        noise_table = self.load_noise_by_substitution_table()
        noise_by_substitution_plot(noise_table)
        assert os.path.exists('noise_by_substitution.pdf')
        os.unlink('./noise_by_substitution.pdf')


if __name__ == '__main__':
    unittest.main()
