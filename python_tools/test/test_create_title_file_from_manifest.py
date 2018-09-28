import os
import unittest

from python_tools.pipeline_kickoff import create_title_file_from_manifest


class Tests(unittest.TestCase):

    def setUp(self):
        pass

    def test_create_title_file(self):
        create_title_file_from_manifest.create_title_file(
            '../../test/test_data/umi-T_N-PanCancer/test_manifest.xlsx',
            './test_title_file.txt'
        )

        assert os.path.exists('./test_title_file.txt')
