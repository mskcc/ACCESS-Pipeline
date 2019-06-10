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
        # Allow us to use paths relative to the current directory's tests
        os.chdir('test__generate_access_variants_inputs')

        self.matched_testing_parameters = {
            'project_name':                     'test_project',
            'matched_mode':                     'True',
            'output_file_name':                 './test_output/ACCESS_Variants_test_inputs.yaml',
            'tumor_bams_directory':             './test_data/tumor_bams',
            'normal_bams_directory':            './test_data/normal_bams',
            'simplex_bams_directory':           './test_data/simplex_bams',
            'curated_bams_duplex_directory':    './test_data/curated_bams_duplex',
            'curated_bams_simplex_directory':   './test_data/curated_bams_simplex',
            'pairing_file_path':                './test_data/test_pairing.tsv',
            'default_normal_path':              './test_data/default_normal.bam',
        }

        # Convert to absolute paths
        self.matched_testing_parameters = {
            k: os.path.abspath(v) for k, v in self.matched_testing_parameters.items()
        }

        # New copies of the arguments dict for different tests
        self.unmatched_testing_parameters = dict(self.matched_testing_parameters)
        self.unmatched_testing_parameters['matched_mode'] = ''

        self.missing_tumor_testing_parameters = dict(self.matched_testing_parameters)
        self.missing_tumor_testing_parameters['pairing_file_path']  = './test_data/test_pairing_missing_tumor.tsv'

        self.missing_normal_testing_parameters = dict(self.matched_testing_parameters)
        self.missing_normal_testing_parameters['pairing_file_path']  = './test_data/test_pairing_missing_normal.tsv'

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


    def test_matched_mode(self):
        """
        End to end inputs creation script test

        :return:
        """
        mock_args = ArgparseMock(self.matched_testing_parameters)
        create_inputs_file(mock_args)

        inputs_file = open(self.matched_testing_parameters['output_file_name'], 'r').read()
        inputs_file = ruamel.yaml.round_trip_load(inputs_file)

        expected_result = open('./expected_results/matched_mode_inputs_result.yaml', 'r').read()
        expected_result = ruamel.yaml.round_trip_load(expected_result)
        assert inputs_file == expected_result


    def test_unmatched_mode(self):
        """
        e2e test for unmatched mode

        :return:
        """
        mock_args = ArgparseMock(self.unmatched_testing_parameters)
        create_inputs_file(mock_args)

        inputs_file = open(self.unmatched_testing_parameters['output_file_name'], 'r').read()
        inputs_file = ruamel.yaml.round_trip_load(inputs_file)

        expected_result = open('./expected_results/unmatched_mode_inputs_result.yaml', 'r').read()
        expected_result = ruamel.yaml.round_trip_load(expected_result)
        assert inputs_file == expected_result


    def test_missing_tumor_bam_throws_error(self):
        """
        tumor_id in pairing file does not have corresponding tumor bam file

        :return:
        """
        mock_args = ArgparseMock(self.missing_tumor_testing_parameters)
        with self.assertRaises(AssertionError):
            create_inputs_file(mock_args)


    def test_missing_normal_bam_throws_error(self):
        """
        tumor_id in pairing file does not have corresponding tumor bam file

        :return:
        """
        mock_args = ArgparseMock(self.missing_normal_testing_parameters)
        with self.assertRaises(AssertionError):
            create_inputs_file(mock_args)
