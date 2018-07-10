import shutil
import unittest

from constants import *
from python_tools.workflow_tools import pipeline_postprocessing


class Tests(unittest.TestCase):

    def setUp(self):
        self.test_dir = './test_data/pipeline_output'
        self.test_outputs_copied = './test_outputs_copied'

        if os.path.exists(self.test_outputs_copied):
            shutil.rmtree(self.test_outputs_copied)

        shutil.copytree(self.test_dir, self.test_outputs_copied)

    def tearDown(self):
        shutil.rmtree(self.test_outputs_copied)

    def test_symlink_bams(self):
        '''
        Method should create folder with symlinks to pipeline bam and bai outputs

        :return:
        '''
        pipeline_postprocessing.symlink_bams(self.test_outputs_copied)
        directories = os.listdir(self.test_outputs_copied)

        assert STANDARD_BAM_DIR in directories
        assert UNFILTERED_BAM_DIR in directories
        assert SIMPLEX_DUPLEX_BAM_DIR in directories
        assert DUPLEX_BAM_DIR in directories

    def test_delete_extraneous_output_folders(self):
        '''
        Method should delete Toil temp dirs

        :return:
        '''
        pipeline_postprocessing.delete_extraneous_output_folders(self.test_outputs_copied)
        directories_remaining = os.listdir(self.test_outputs_copied)

        for dir in directories_remaining:
            assert not TMPDIR_SEARCH.match(dir)
            assert not OUT_TMPDIR_SEARCH.match(dir)


if __name__ == '__main__':
    unittest.main()
