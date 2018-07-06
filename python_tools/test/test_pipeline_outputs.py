import os
import re
import sys
import logging
import unittest


########
# This TestCase is meant to be run after a successful Toil run,
# to check that all output files are found, and located in the correct sample folders
#
# Usage: python test_pipeline_outputs.py /path/to/toil/outputs
#
# Todo: Set up end-to-end test that calls this script automatically


# Set up logging
logger = logging.getLogger('outputs_test')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)



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
        """
        Check that each sample folder has the files that we would expect to get for that sample
        from the pipeline run

        :return:
        """
        subfolders = [x[0] for x in os.walk(self.output_dir)]

        for folder in subfolders:
            print(folder)

            files = os.listdir(os.path.join(self.output_dir, folder))

            if 'umi_clipping_results' in folder:
                logger.info('Testing results folder: {}'.format(folder))
                logger.info('With files: {}'.format(files))

                # UMI Clipping results folder
                assert 'composite-umi-frequencies.txt' in files
                assert 'info.txt' in files
                assert 'SampleSheet.csv' in files
                assert 'umi-frequencies.txt' in files

                self.assertTrue(substring_in_list('_R1_001.fastq.gz', files))
                self.assertTrue(substring_in_list('_R2_001.fastq.gz', files))

            if re.compile(r'^Sample_').match(folder.replace('./', '')):
                logger.info('Testing results folder: {}'.format(folder))
                logger.info('With files: {}'.format(files))

                # Standard + Collapsed bams folder
                sample_id = folder.split('/')[-1]
                sample_id = re.sub(r'^Sample_', '', sample_id)

                assert 'collapsed_R1_.fastq.gz' in files
                assert 'collapsed_R2_.fastq.gz' in files
                assert 'first-pass-alt-alleles.txt' in files
                assert 'first-pass.mate-position-sorted.txt' in files
                assert 'first-pass.txt' in files
                assert 'second-pass-alt-alleles.txt' in files

                # All bams should be found
                self.assertTrue(substring_in_list('__aln_srt_IR_FX.bam', files))
                self.assertTrue(substring_in_list('__aln_srt_IR_FX.bai', files))
                self.assertTrue(substring_in_list('__aln_srt_IR_FX-duplex.bam', files))
                self.assertTrue(substring_in_list('__aln_srt_IR_FX-duplex.bai', files))
                self.assertTrue(substring_in_list('__aln_srt_IR_FX-simplex-duplex.bam', files))
                self.assertTrue(substring_in_list('__aln_srt_IR_FX-simplex-duplex.bai', files))
                self.assertTrue(substring_in_list('_cl_aln_srt_MD_IR_FX_BR.bam', files))
                self.assertTrue(substring_in_list('_cl_aln_srt_MD_IR_FX_BR.bai', files))

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