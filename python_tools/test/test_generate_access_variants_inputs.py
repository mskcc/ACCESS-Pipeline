import os
import shutil
import unittest
import ruamel.yaml

from python_tools.pipeline_kickoff.generate_access_variants_inputs import (
    create_inputs_file,
    create_yaml_file_objects
)
from util import ArgparseMock


class CreateInputsFromBamDirectoryTestCase(unittest.TestCase):


    def setUp(self):
        """
        Set some constants used for testing

        :return:
        """
        self.matched_testing_parameters = {
            'matched_mode':                 'True',
            'output_file_name':             './test_output/ACCESS_Variants_test_inputs.yaml',
            'tumor_bams_directory':         './test_data/tumor_bams',
            'normal_bams_directory':        './test_data/normal_bams',
            'simplex_bams_directory':       './test_data/simplex_bams',
            'curated_bams_directory':       './test_data/curated_bams',
            'pairing_file_path':            './test_data/test_pairing.tsv',
            'default_normal_path':          './test_data/default_normal.bam',
        }
        self.unmatched_testing_parameters = {
            'matched_mode':                 '',
            'output_file_name':             './test_output/ACCESS_Variants_test_inputs.yaml',
            'tumor_bams_directory':         './test_data/tumor_bams',
            'normal_bams_directory':        './test_data/normal_bams',
            'simplex_bams_directory':       './test_data/simplex_bams',
            'curated_bams_directory':       './test_data/curated_bams',
            'pairing_file_path':            './test_data/test_pairing.tsv',
            'default_normal_path':           './test_data/default_normal.bam',
        }

        # Set up test outputs directr=ory
        os.mkdir('./test_output')


    def tearDown(self):
        """
        Remove test outputs after each test

        :return:
        """
        shutil.rmtree('./test_output')


    def test_matched_mode(self):
        """
        End to end inputs creation script test

        :return:
        """
        mock_args = ArgparseMock(self.matched_testing_parameters)
        create_inputs_file(mock_args)

        inputs_file = open(self.matched_testing_parameters['output_file_name'], 'r').read()
        inputs_file = ruamel.yaml.round_trip_load(inputs_file)

        assert len(inputs_file['tumor_bams']) == 3
        assert len(inputs_file['normal_bams']) == 3
        assert len(inputs_file['tumor_sample_names']) == 3
        assert len(inputs_file['normal_sample_names']) == 3
        assert len(inputs_file['genotyping_bams']) == 11

        assert inputs_file['tumor_bams'][0] == {'class': 'File', 'path': './test_data/tumor_bams/tumor_bam_1.bam'}
        assert inputs_file['tumor_bams'][1] == {'class': 'File', 'path': './test_data/tumor_bams/tumor_bam_2.bam'}
        assert inputs_file['tumor_bams'][2] == {'class': 'File', 'path': './test_data/tumor_bams/tumor_bam_3.bam'}

        assert inputs_file['normal_bams'][0] == {'class': 'File', 'path': './test_data/normal_bams/normal_bam_1.bam'}
        # T2 bam is missing a matched normal --> test that default normal is used instead
        assert inputs_file['normal_bams'][1] == {'class': 'File', 'path': './test_data/default_normal.bam'}
        assert inputs_file['normal_bams'][2] == {'class': 'File', 'path': './test_data/normal_bams/normal_bam_3.bam'}

        # Test the fillout bams list
        assert inputs_file['genotyping_bams'][0] == {'class': 'File', 'path': './test_data/tumor_bams/tumor_bam_1.bam'}
        assert inputs_file['genotyping_bams'][1] == {'class': 'File', 'path': './test_data/normal_bams/normal_bam_1.bam'}
        assert inputs_file['genotyping_bams'][2] == {'class': 'File', 'path': './test_data/tumor_bams/tumor_bam_2.bam'}
        assert inputs_file['genotyping_bams'][3] == {'class': 'File', 'path': './test_data/tumor_bams/tumor_bam_3.bam'}
        assert inputs_file['genotyping_bams'][4] == {'class': 'File', 'path': './test_data/normal_bams/normal_bam_3.bam'}
        assert inputs_file['genotyping_bams'][5] == {'class': 'File', 'path': './test_data/simplex_bams/simplex_bam_1.bam'}
        assert inputs_file['genotyping_bams'][6] == {'class': 'File', 'path': './test_data/simplex_bams/simplex_bam_2.bam'}
        assert inputs_file['genotyping_bams'][7] == {'class': 'File', 'path': './test_data/simplex_bams/simplex_bam_3.bam'}
        assert inputs_file['genotyping_bams'][8] == {'class': 'File', 'path': './test_data/curated_bams/curated_bam_1.bam'}
        assert inputs_file['genotyping_bams'][9] == {'class': 'File', 'path': './test_data/curated_bams/curated_bam_2.bam'}
        assert inputs_file['genotyping_bams'][10] == {'class': 'File', 'path': './test_data/curated_bams/curated_bam_3.bam'}


    def test_unmatched_mode(self):
        """
        e2e test for unmatched mode

        :return:
        """
        mock_args = ArgparseMock(self.unmatched_testing_parameters)
        create_inputs_file(mock_args)

        inputs_file = open(self.unmatched_testing_parameters['output_file_name'], 'r').read()
        inputs_file = ruamel.yaml.round_trip_load(inputs_file)

        assert len(inputs_file['tumor_bams']) == 3
        assert len(inputs_file['normal_bams']) == 3
        assert len(inputs_file['tumor_sample_names']) == 3
        assert len(inputs_file['normal_sample_names']) == 3
        assert len(inputs_file['genotyping_bams']) == 11

        assert inputs_file['tumor_bams'][0] == {'class': 'File', 'path': './test_data/tumor_bams/tumor_bam_1.bam'}
        assert inputs_file['tumor_bams'][1] == {'class': 'File', 'path': './test_data/tumor_bams/tumor_bam_2.bam'}
        assert inputs_file['tumor_bams'][2] == {'class': 'File', 'path': './test_data/tumor_bams/tumor_bam_3.bam'}

        assert inputs_file['normal_bams'][0] == {'class': 'File', 'path': './test_data/default_normal.bam'}
        assert inputs_file['normal_bams'][1] == {'class': 'File', 'path': './test_data/default_normal.bam'}
        assert inputs_file['normal_bams'][2] == {'class': 'File', 'path': './test_data/default_normal.bam'}

        # Test the fillout bams list
        assert inputs_file['genotyping_bams'][0] == {'class': 'File', 'path': './test_data/tumor_bams/tumor_bam_1.bam'}
        assert inputs_file['genotyping_bams'][1] == {'class': 'File', 'path': './test_data/normal_bams/normal_bam_1.bam'}
        assert inputs_file['genotyping_bams'][2] == {'class': 'File', 'path': './test_data/tumor_bams/tumor_bam_2.bam'}
        assert inputs_file['genotyping_bams'][3] == {'class': 'File', 'path': './test_data/tumor_bams/tumor_bam_3.bam'}
        assert inputs_file['genotyping_bams'][4] == {'class': 'File', 'path': './test_data/normal_bams/normal_bam_3.bam'}
        assert inputs_file['genotyping_bams'][5] == {'class': 'File', 'path': './test_data/simplex_bams/simplex_bam_1.bam'}
        assert inputs_file['genotyping_bams'][6] == {'class': 'File', 'path': './test_data/simplex_bams/simplex_bam_2.bam'}
        assert inputs_file['genotyping_bams'][7] == {'class': 'File', 'path': './test_data/simplex_bams/simplex_bam_3.bam'}
        assert inputs_file['genotyping_bams'][8] == {'class': 'File', 'path': './test_data/curated_bams/curated_bam_1.bam'}
        assert inputs_file['genotyping_bams'][9] == {'class': 'File', 'path': './test_data/curated_bams/curated_bam_2.bam'}
        assert inputs_file['genotyping_bams'][10] == {'class': 'File', 'path': './test_data/curated_bams/curated_bam_3.bam'}
