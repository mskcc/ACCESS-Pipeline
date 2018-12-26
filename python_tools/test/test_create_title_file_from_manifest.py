import shutil
import unittest

from constants import *
from util import read_df
from python_tools.pipeline_kickoff import create_title_file_from_manifest


class CTFMTests(unittest.TestCase):

    def setUp(self):
        os.mkdir('./test_output')

    def tearDown(self):
        shutil.rmtree('./test_output')

    def test_create_title_file(self):
        create_title_file_from_manifest.create_title_file(
            '../../test/test_data/umi-T_N-PanCancer/test_manifest.xlsx',
            './test_output/test_title_file.txt'
        )

        assert os.path.exists('./test_output/test_title_file.txt')

    def test_create_title_file_multiple_lanes(self):
        create_title_file_from_manifest.create_title_file(
            './test_data/test_manifests/test_manifest_multilane.xlsx',
            './test_output/test_title_file.txt'
        )

        assert os.path.exists('./test_output/Test_Project_1_test_title_file.txt')
        assert os.path.exists('./test_output/Test_Project_2_test_title_file.txt')

    def test_sample_id_renaming(self):
        create_title_file_from_manifest.create_title_file(
            '../../test/test_data/umi-T_N-PanCancer/test_manifest.xlsx',
            './test_output/test_title_file.txt'
        )

        title_file = read_df('./test_output/test_title_file.txt', header='infer')
        # Test that SampleRenames column was used correctly
        assert title_file.ix[0, SAMPLE_ID_COLUMN] == 'test_sample_1a'


if __name__ == '__main__':
    unittest.main()