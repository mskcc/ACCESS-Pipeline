import os
import shutil
import unittest

from python_tools.pipeline_kickoff import create_title_file_from_manifest


class Tests(unittest.TestCase):

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

        assert os.path.exists('./test_output/lane-1_test_title_file.txt')
        assert os.path.exists('./test_output/lane-2_test_title_file.txt')
