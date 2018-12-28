import os
import shutil
import unittest

from workflow_tools.ACCESS_filters import (
    make_per_filtered_maf,
    apply_filter_maf
)

from util import ArgparseMock


class CreateInputsFromBamDirectoryTestCase(unittest.TestCase):


    def setUp(self):
        """
        Set some constants used for testing

        :return:
        """
        # Allow us to use paths relative to the current directory's tests
        # os.chdir('test__ACCESS_Filters')

        self.testing_parameters = {
            'anno_maf':                                 './test_data/MSK-L-115_T.MSK-L-115_N.combined-variants.vep_taggedHotspots_rmv.maf',
            'fillout_maf':                              './test_data/MSK-L-115_T.MSK-L-115_N.combined-variants.vep_taggedHotspots_rmv_fillout.maf',
            'tumor_samplename':                         'MSK-L-115_T_S1_001',
            'normal_samplename':                        'MSK-L-115_N_S7_001',
            'tumor_detect_alt_thres':                   2,
            'curated_detect_alt_thres':                 2,
            'DS_tumor_detect_alt_thres':                2,
            'DS_curated_detect_alt_thres':              2,

            'normal_TD_min':                            20,
            'normal_vaf_germline_thres':                0.4,
            'tumor_TD_min':                             20,
            'tumor_vaf_germline_thres':                 0.4,
            'tier_one_alt_min':                         3,
            'tier_two_alt_min':                         5,
            'min_n_curated_samples_alt_detected':       2,
            'tn_ratio_thres':                           5,
        }

        self.testing_parameters_mismatching_sample_id = dict(self.testing_parameters)
        self.testing_parameters_mismatching_sample_id['tumor_samplename'] = 'MSK-L-115_T'


        # Convert to absolute paths
        # self.testing_parameters = {
        #     k: os.path.abspath(v) for k, v in self.testing_parameters.items()
        # }

        # Set up test outputs directory
        # os.mkdir('./test_output')


    def tearDown(self):
        """
        Remove test outputs after each test

        :return:
        """
        # shutil.rmtree('./test_output')

        # Move back up to main test dir
        # os.chdir('..')


    def test_access_filters(self):
        """
        End to end inputs creation script test

        :return:
        """
        mock_args = ArgparseMock(self.testing_parameters)

        df_pre_filter = make_per_filtered_maf(mock_args)
        df_post_filter = apply_filter_maf(df_pre_filter, mock_args)

        # assert df_post_filter['some_passing_mutation', 'status'] == 'Tier 1'
        # assert df_post_filter['another_passing_mutation', 'status'] == 'Tier 2'


    def test_mismatching_tumor_sample_id(self):
        """
        End to end inputs creation script test

        :return:
        """
        mock_args = ArgparseMock(self.testing_parameters_mismatching_sample_id)

        with self.assertRaises(Exception):
            df_pre_filter = make_per_filtered_maf(mock_args)
            df_post_filter = apply_filter_maf(df_pre_filter, mock_args)
