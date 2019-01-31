import shutil
import unittest

from python_tools.constants import *
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

        assert 'EDA-23Jd_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-duplex.bai' in os.listdir('./test_outputs_copied/duplex_bams')
        assert 'EDA-23Jd_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-duplex.bam' in os.listdir('./test_outputs_copied/duplex_bams')
        assert 'FAC-2Je3_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-duplex.bai' in os.listdir('./test_outputs_copied/duplex_bams')
        assert 'FAC-2Je3_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-duplex.bam' in os.listdir('./test_outputs_copied/duplex_bams')

        assert STANDARD_BAM_DIR in directories
        assert UNFILTERED_BAM_DIR in directories
        assert SIMPLEX_BAM_DIR in directories
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

    def test_move_markduplicates_files(self):
        """

        :return:
        """
        pipeline_postprocessing.move_markduplicates_files(self.test_outputs_copied)
        directories_remaining = os.listdir(self.test_outputs_copied)

        # Folder should exist
        assert any([MARK_DUPLICATES_FILES_DIR in dir for dir in directories_remaining])

        md_files = os.listdir(os.path.join(self.test_outputs_copied, MARK_DUPLICATES_FILES_DIR))
        assert len(md_files) > 0

        # Files inside should have md suffix
        for f in md_files:
            assert MARK_DUPLICATES_FILE_SEARCH.match(f)

    def test_move_trim_files(self):
        """

        :return:
        """
        pipeline_postprocessing.move_trim_files(self.test_outputs_copied)
        directories_remaining = os.listdir(self.test_outputs_copied)

        # Folder should exist
        assert any([TRIM_FILES_DIR in dir for dir in directories_remaining])

        trim_files = os.listdir(os.path.join(self.test_outputs_copied, TRIM_FILES_DIR))
        assert len(trim_files) > 0

        # Files inside should have trim suffix
        for f in trim_files:
            assert TRIM_FILE_SEARCH.match(f)

    def test_move_covered_intervals_files(self):
        """

        :return:
        """
        pipeline_postprocessing.move_covered_intervals_files(self.test_outputs_copied)
        directories_remaining = os.listdir(self.test_outputs_copied)

        # Folder should exist
        assert any([COVERED_INTERVALS_DIR in dir for dir in directories_remaining])

        ci_files = os.listdir(os.path.join(self.test_outputs_copied, COVERED_INTERVALS_DIR))
        assert len(ci_files) > 0

        for f in ci_files:
            assert COVERED_INTERVALS_FILE_SEARCH.match(f)



if __name__ == '__main__':
    unittest.main()
