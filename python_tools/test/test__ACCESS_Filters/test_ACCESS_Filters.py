import unittest

from workflow_tools.ACCESS_filters import (
    make_pre_filtered_maf,
    apply_filter_maf,
    make_condensed_post_filter
)

from util import ArgparseMock


class ACCESSFiltersTestCase(unittest.TestCase):


    def setUp(self):
        """
        Set some constants used for testing

        :return:
        """
        # Allow us to use paths relative to the current directory's tests
        # os.chdir('test__ACCESS_Filters')

        self.testing_parameters = {
            'tumor_samplename':                         't_sample',
            'normal_samplename':                        'n_sample',
            'anno_maf':                                 './test_data/test.maf',
            'fillout_maf':                              './test_data/test_fillout.maf',
            'blacklist':                                './test_data/blacklist.txt',
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


        self.testing_parameters_seracare = {
            'tumor_samplename':                         'SeraCare_0-5',
            'normal_samplename':                        'F22',
            'anno_maf':                                 './test_data/SeraCare_0-5/SeraCare_0-5.F22.combined-variants.vep_keptrmv_taggedHotspots.maf',
            'fillout_maf':                              './test_data/SeraCare_0-5/SeraCare_0-5.F22.combined-variants.vep_keptrmv_taggedHotspots_fillout.maf',
            'blacklist':                                './test_data/blacklist.txt',
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

        df_pre_filter = make_pre_filtered_maf(mock_args)
        df_post_filter = apply_filter_maf(df_pre_filter, mock_args.blacklist, mock_args)

        # Todo: Validate and use this test data
        # assert df_post_filter.loc[('1', 8080157, 8080157, 'T', 'A',)]['Status'] == 'TNRatio-curatedmedian;TNRatio-matchnorm;NonExonic;'
        # assert df_post_filter.loc[('17', 37882882, 37882882, 'C', 'A',)]['Status'] == 'NotTiered;NonExonic;'
        # assert df_post_filter.loc[('18', 48584855, 48584855, 'A', 'TTT',)]['Status'] == 'NonExonic;'
        # assert df_post_filter.loc[('18', 48584872, 48584872, 'G', 'T',)]['Status'] == 'NotTiered;NonExonic;'
        # assert df_post_filter.loc[('18', 48586244, 48586244, 'C', 'T',)]['Status'] == 'NotTiered;'
        # assert df_post_filter.loc[('18', 57571783, 57571783, 'T', '-',)]['Status'] == 'NotTiered;TNRatio-curatedmedian;TNRatio-matchnorm;NonExonic;'
        # assert df_post_filter.loc[('18', 57571784, 57571784, 'C', '-',)]['Status'] == 'NonExonic;'
        # assert df_post_filter.loc[('19', 10273379, 10273379, 'A', 'T',)]['Status'] == 'TNRatio-curatedmedian;TNRatio-matchnorm;'

    def test_access_filters_seracare(self):
        """
        E2E test with SeraCare sample maf and fillout

        :return:
        """
        mock_args = ArgparseMock(self.testing_parameters_seracare)

        df_pre_filter = make_pre_filtered_maf(mock_args)
        df_post_filter = apply_filter_maf(df_pre_filter, mock_args.blacklist, mock_args)
        condensed = make_condensed_post_filter(df_post_filter)


    def test_mismatching_tumor_sample_id(self):
        """
        End to end inputs creation script test

        :return:
        """
        mock_args = ArgparseMock(self.testing_parameters_mismatching_sample_id)

        with self.assertRaises(Exception):
            df_pre_filter = make_pre_filtered_maf(mock_args)
            df_post_filter = apply_filter_maf(df_pre_filter, mock_args.blacklist, mock_args)
