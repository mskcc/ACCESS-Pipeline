import os
import sys
import unittest


########
# This TestCase is meant to be run after a successful Toil run,
# to check that all output files are found, and located in the correct sample folders
#
# Usage: python test_pipeline_outputs.py /path/to/toil/outputs
#
# Todo: Set up end-to-end test that calls this script automatically


def substring_in_list(substring, list):
    """
    Look for `substring` in each element in `list`

    :param substring: substring to look for
    :param list: elements to find substring in
    :return: True / False if found / not found
    """
    for elem in list:
        if substring in elem:
            return True
    return False

def substrings_in_list(substrings, list):
    """
    Check to see that all elements from `substrings` can be found together in a single element of `list`
    """
    for elem in list:
        founds = []
        for substring in substrings:
            founds.append(substring in elem)
        if all(founds):
            return True
    return False


class TestPipelineOutputs(unittest.TestCase):

    output_dir = ''

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_folders_have_all_correct_files(self):

        for folder in os.listdir(self.output_dir):

            files = os.listdir(os.path.join(self.output_dir, folder))

            if 'umi_clipping_results' in folder:
                # UMI Clipping results folder
                assert 'composite-umi-frequencies.txt' in files
                assert 'info.txt' in files
                assert 'SampleSheet.csv' in files
                assert 'umi-frequencies.txt' in files

                self.assertTrue(substring_in_list('_R1_001.fastq.gz', files))
                self.assertTrue(substring_in_list('_R2_001.fastq.gz', files))

            if 'Sample_' in folder:
                # Standard + Collapsed bams folder
                sample_id = folder.replace('Sample_', '')

                assert 'collapsed_R1_.fastq.gz' in files
                assert 'collapsed_R2_.fastq.gz' in files
                assert 'first-pass-alt-alleles.txt' in files
                assert 'first-pass.mate-position-sorted.txt' in files
                assert 'first-pass.txt' in files
                assert 'second-pass-alt-alleles.txt' in files

                # All bams should be found, with correct sample_ids
                self.assertTrue(substrings_in_list(['__aln_srt_IR_FX.bam', sample_id], files))
                self.assertTrue(substrings_in_list(['__aln_srt_IR_FX.bai', sample_id], files))
                self.assertTrue(substrings_in_list(['__aln_srt_IR_FX-duplex.bam', sample_id], files))
                self.assertTrue(substrings_in_list(['__aln_srt_IR_FX-duplex.bai', sample_id], files))
                self.assertTrue(substrings_in_list(['__aln_srt_IR_FX-simplex-duplex.bam', sample_id], files))
                self.assertTrue(substrings_in_list(['__aln_srt_IR_FX-simplex-duplex.bai', sample_id], files))
                self.assertTrue(substrings_in_list(['_cl_aln_srt_MD_IR_FX_BR.bam', sample_id], files))
                self.assertTrue(substrings_in_list(['_cl_aln_srt_MD_IR_FX_BR.bai', sample_id], files))

def main():
    TestPipelineOutputs.output_dir = sys.argv.pop()
    unittest.main()

if __name__ == '__main__':
    main()