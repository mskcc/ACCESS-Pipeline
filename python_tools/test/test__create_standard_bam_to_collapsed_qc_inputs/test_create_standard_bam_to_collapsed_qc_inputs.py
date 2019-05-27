import os
import shutil
import unittest
import ruamel.yaml as yaml

from util import ArgparseMock
import python_tools.pipeline_kickoff.create_standard_bam_to_collapsed_qc_inputs as csbtcqi


class CreateInputsFromBamDirectoryTestCase(unittest.TestCase):


    def setUp(self):
        """
        Set some constants used for testing

        :return:
        """
        # Allow us to use paths relative to the current directory's tests
        # os.chdir('test__create_standard_bam_to_collapsed_qc_inputs')

        self.testing_params = {
            'project_name':                     'test_project',
            'output_file_name':                 './test_output/ACCESS_Variants_test_inputs.yaml',
            'standard_bams_directory':          './test_data/standard_bams',
            'title_file_path':                  './test_data/title_file.txt'
        }

        # Convert to absolute paths
        self.testing_params = {
            k: os.path.abspath(v) for k, v in self.testing_params.items()
        }

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


    def test_missing_normal_bam_throws_error(self):
        """
        tumor_id in pairing file does not have corresponding tumor bam file

        :return:
        """
        mock_args = ArgparseMock(self.testing_params)
        csbtcqi.write_inputs_yaml(mock_args)


        expected = yaml.round_trip_load(open('./expected_results/standard_bams_to_collapsed_qc_inputs.yaml').read())
        actual = yaml.round_trip_load(open(self.testing_params['output_file_name']).read())
        assert actual == expected
