import unittest

from python_tools.workflow_tools.check_pipeline_outputs import (
    test_folders_have_all_correct_files,
    test_rg_id_matches_sample_id
)


class CheckPipelineOutputsTestCase(unittest.TestCase):

    def test_check_folders_have_all_correct_files(self):
        """
        Test check for sample folders having correct files

        :return:
        """
        test_folders_have_all_correct_files('./test_data/')

    def test_check_rg_id_matches_sample_id(self):
        """
        Test check for rg id in bams

        :return:
        """
        test_rg_id_matches_sample_id('./test_data/')


if __name__ == '__main__':
    unittest.main()
