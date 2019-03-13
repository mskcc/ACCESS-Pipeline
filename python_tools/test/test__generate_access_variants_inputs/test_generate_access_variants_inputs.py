import os
import shutil
import unittest
import ruamel.yaml

<<<<<<< HEAD
from python_tools.pipeline_kickoff.generate_access_variants_inputs import (
    create_inputs_file,
)
from python_tools.util import ArgparseMock



class GenerateAccessVariantsInputsTestCase(unittest.TestCase):
=======
from pipeline_kickoff.generate_access_variants_inputs import (
    create_inputs_file,
    create_yaml_file_objects
)
from util import ArgparseMock



class CreateInputsFromBamDirectoryTestCase(unittest.TestCase):

>>>>>>> master

    def setUp(self):
        """
        Set some constants used for testing

        :return:
        """
<<<<<<< HEAD
        self.test_path = os.path.abspath(os.path.dirname(__file__))
=======
        # Allow us to use paths relative to the current directory's tests
        os.chdir('test__generate_access_variants_inputs')
>>>>>>> master

        self.matched_testing_parameters = {
            'project_name':                     'test_project',
            'matched_mode':                     'True',
<<<<<<< HEAD
            'output_file_name':                 self.test_path + '/test_output/_',
            'tumor_bams_directory':             self.test_path + '/test_data/tumor_bams',
            'normal_bams_directory':            self.test_path + '/test_data/normal_bams',
            'simplex_bams_directory':           self.test_path + '/test_data/simplex_bams',
            'curated_bams_duplex_directory':    self.test_path + '/test_data/curated_bams_duplex',
            'curated_bams_simplex_directory':   self.test_path + '/test_data/curated_bams_simplex',
            'pairing_file_path':                self.test_path + '/test_data/test_pairing.tsv',
            'default_normal_path':              self.test_path + '/test_data/default_normal_cl_aln_srt_MD_IR_FX_BR.bam',
            'structural_variants':              False,
=======
            'output_file_name':                 './test_output/ACCESS_Variants_test_inputs.yaml',
            'tumor_bams_directory':             './test_data/tumor_bams',
            'normal_bams_directory':            './test_data/normal_bams',
            'simplex_bams_directory':           './test_data/simplex_bams',
            'curated_bams_duplex_directory':    './test_data/curated_bams_duplex',
            'curated_bams_simplex_directory':   './test_data/curated_bams_simplex',
            'pairing_file_path':                './test_data/test_pairing.tsv',
            'default_normal_path':              './test_data/default_normal.bam',
>>>>>>> master
        }

        # Convert to absolute paths
        self.matched_testing_parameters = {
<<<<<<< HEAD
            k: os.path.abspath(v) if (type(v) == str) and ('/test' in v) else v for k, v in self.matched_testing_parameters.items()
        }

        self.missing_tumor_testing_parameters = dict(self.matched_testing_parameters)
        self.missing_tumor_testing_parameters['pairing_file_path']  = self.test_path + '/test_data/test_pairing_missing_tumor.tsv'

        self.missing_normal_testing_parameters = dict(self.matched_testing_parameters)
        self.missing_normal_testing_parameters['pairing_file_path']  = self.test_path + '/test_data/test_pairing_missing_normal.tsv'

        # Check bam & ID-related fields
        # Todo: include unittests for parameters & tools
        self._fields_to_check = [
            'tumor_bams',
            'normal_bams',
            'tumor_sample_names',
            'normal_sample_names',
            'matched_normal_ids',
            'genotyping_bams',
            'genotyping_bams_ids',
        ]
=======
            k: os.path.abspath(v) for k, v in self.matched_testing_parameters.items()
        }

        # New copies of the arguments dict for different tests
        self.unmatched_testing_parameters = dict(self.matched_testing_parameters)
        self.unmatched_testing_parameters['matched_mode'] = ''

        self.missing_tumor_testing_parameters = dict(self.matched_testing_parameters)
        self.missing_tumor_testing_parameters['pairing_file_path']  = './test_data/test_pairing_missing_tumor.tsv'

        self.missing_normal_testing_parameters = dict(self.matched_testing_parameters)
        self.missing_normal_testing_parameters['pairing_file_path']  = './test_data/test_pairing_missing_normal.tsv'
>>>>>>> master

        # Set up test outputs directory
        os.mkdir('./test_output')


    def tearDown(self):
        """
        Remove test outputs after each test

        :return:
        """
        shutil.rmtree('./test_output')

<<<<<<< HEAD
=======
        # Move back up to main test dir
        os.chdir('..')

>>>>>>> master

    def test_matched_mode(self):
        """
        End to end inputs creation script test

        :return:
        """
<<<<<<< HEAD
        self.matched_testing_parameters['output_file_name'] = './test_output/matched_mode_inputs_result.yaml'
=======
>>>>>>> master
        mock_args = ArgparseMock(self.matched_testing_parameters)
        create_inputs_file(mock_args)

        inputs_file = open(self.matched_testing_parameters['output_file_name'], 'r').read()
        inputs_file = ruamel.yaml.round_trip_load(inputs_file)

<<<<<<< HEAD
        expected_result_path = self.test_path + '/expected_results/matched_mode_inputs_result.yaml'
        expected_result = open(expected_result_path, 'r').read()
        expected_result = ruamel.yaml.round_trip_load(expected_result)

        for key in self._fields_to_check:
            assert inputs_file[key] == expected_result[key]
=======
        expected_result = open('./expected_results/matched_mode_inputs_result.yaml', 'r').read()
        expected_result = ruamel.yaml.round_trip_load(expected_result)
        assert inputs_file == expected_result
>>>>>>> master


    def test_unmatched_mode(self):
        """
        e2e test for unmatched mode

        :return:
        """
<<<<<<< HEAD
        # New copies of the arguments dict for different tests
        self.unmatched_testing_parameters = dict(self.matched_testing_parameters)
        self.unmatched_testing_parameters['matched_mode'] = ''

        self.unmatched_testing_parameters['output_file_name'] = './test_output/unmatched_mode_inputs_result.yaml'
=======
>>>>>>> master
        mock_args = ArgparseMock(self.unmatched_testing_parameters)
        create_inputs_file(mock_args)

        inputs_file = open(self.unmatched_testing_parameters['output_file_name'], 'r').read()
        inputs_file = ruamel.yaml.round_trip_load(inputs_file)

<<<<<<< HEAD
        expected_result_path = self.test_path + '/expected_results/unmatched_mode_inputs_result.yaml'
        expected_result = open(expected_result_path, 'r').read()
        expected_result = ruamel.yaml.round_trip_load(expected_result)

        for key in self._fields_to_check:
            assert inputs_file[key] == expected_result[key]


    def test_matched_mode_without_pairing_file(self):
        """
        e2e test for matched mode without pairing file

        :return:
        """
        self.matched_testing_parameters['output_file_name'] = './test_output/matched_mode_no_pairing_file_inputs_result.yaml'
        self.matched_testing_parameters['pairing_file_path'] = None
        mock_args = ArgparseMock(self.matched_testing_parameters)

        with self.assertRaises(Exception):
            create_inputs_file(mock_args)


    def test_unmatched_mode_without_pairing_file(self):
        """
        e2e test for unmatched mode without pairing file

        :return:
        """
        # New copies of the arguments dict for different tests
        self.unmatched_testing_parameters = dict(self.matched_testing_parameters)
        self.unmatched_testing_parameters['matched_mode'] = ''

        self.unmatched_testing_parameters['output_file_name'] = './test_output/unmatched_mode_no_pairing_file_inputs_result.yaml'
        self.unmatched_testing_parameters['pairing_file_path'] = None
        mock_args = ArgparseMock(self.unmatched_testing_parameters)
        create_inputs_file(mock_args)

        inputs_file = open(self.unmatched_testing_parameters['output_file_name'], 'r').read()
        inputs_file = ruamel.yaml.round_trip_load(inputs_file)

        expected_result_path = self.test_path + '/expected_results/unmatched_mode_no_pairing_file_inputs_result.yaml'
        expected_result = open(expected_result_path, 'r').read()
        expected_result = ruamel.yaml.round_trip_load(expected_result)

        for key in self._fields_to_check:
            assert inputs_file[key] == expected_result[key]
=======
        expected_result = open('./expected_results/unmatched_mode_inputs_result.yaml', 'r').read()
        expected_result = ruamel.yaml.round_trip_load(expected_result)
        assert inputs_file == expected_result
>>>>>>> master


    def test_missing_tumor_bam_throws_error(self):
        """
        tumor_id in pairing file does not have corresponding tumor bam file

        :return:
        """
<<<<<<< HEAD
        self.missing_tumor_testing_parameters['output_file_name'] = './test_output/should_error.yaml'
=======
>>>>>>> master
        mock_args = ArgparseMock(self.missing_tumor_testing_parameters)
        with self.assertRaises(AssertionError):
            create_inputs_file(mock_args)


    def test_missing_normal_bam_throws_error(self):
        """
        tumor_id in pairing file does not have corresponding tumor bam file

        :return:
        """
<<<<<<< HEAD
        self.missing_normal_testing_parameters['output_file_name'] = './test_output/should_error.yaml'
=======
>>>>>>> master
        mock_args = ArgparseMock(self.missing_normal_testing_parameters)
        with self.assertRaises(AssertionError):
            create_inputs_file(mock_args)
