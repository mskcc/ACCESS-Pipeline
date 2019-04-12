import argparse
import subprocess

from ..util import *


########
# This TestCase is meant to be run after a successful Toil run,
# to check that all output files are found, and located in the correct sample folders
#
# Usage:
# python -m python_tools.workflow_tools.check_pipeline_outputs -o . -l debug
#
# Todo: Set up end-to-end test that calls this script automatically


# Set up logging
logger = logging.getLogger('ACCESS_test')



def test_folders_have_all_correct_files(output_dir):
    """
    Check that each sample folder has the files that we would expect to get for that sample
    from the pipeline run

    :return:
    """
    subfolders = [x for x in os.listdir(output_dir)]
    subfolders = [x for x in subfolders if os.path.isdir(os.path.join(output_dir, x))]
    subfolders = [x for x in subfolders if not 'log' in x]

    # Find the output folders with bams inside
    sample_folders = filter(lambda x: substring_in_list('second-pass-alt-alleles.txt', listdir(output_dir, x)),
                            subfolders)

    for folder in sample_folders:
        files = os.listdir(os.path.join(output_dir, folder))
        # Standard + Collapsed bams folder
        sample_id = folder.split('/')[-1]

        logger.info(folder)
        assert 'collapsed_R1_.fastq.gz' in files
        assert 'collapsed_R2_.fastq.gz' in files
        assert 'first-pass-alt-alleles.txt' in files
        assert 'first-pass.mate-position-sorted.txt' in files
        assert 'first-pass.txt' in files
        assert 'second-pass-alt-alleles.txt' in files

        print(STANDARD_BAM_SEARCH)
        print(sample_id)
        print(files)

        # All bams should be found, with correct sample_ids
        assert substrings_in_list([STANDARD_BAM_SEARCH, sample_id], files)
        assert substrings_in_list([STANDARD_BAI_SEARCH, sample_id], files)
        assert substrings_in_list([UNFILTERED_BAM_SEARCH, sample_id], files)
        assert substrings_in_list([UNFILTERED_BAI_SEARCH, sample_id], files)
        assert substrings_in_list([SIMPLEX_BAM_SEARCH, sample_id], files)
        assert substrings_in_list([SIMPLEX_BAI_SEARCH, sample_id], files)
        assert substrings_in_list([DUPLEX_BAM_SEARCH, sample_id], files)
        assert substrings_in_list([DUPLEX_BAI_SEARCH, sample_id], files)

def test_rg_id_matches_sample_id(output_dir):
    """
    Read group IDs from bams must match the file names and folder in which they are found

    :return:
    """
    # Find the output folders with bams inside
    subfolders = [x for x in os.listdir(output_dir)]
    subfolders = [x for x in subfolders if os.path.isdir(os.path.join(output_dir, x))]
    subfolders = [x for x in subfolders if not 'log' in x]
    sample_folders = filter(lambda x: substring_in_list('second-pass-alt-alleles.txt', listdir(output_dir, x)),
                            subfolders)

    for folder in sample_folders:
        # Find the bam files in this sample folder
        sample_files = os.listdir(os.path.join(output_dir, folder))
        bam_files = [f for f in sample_files if '.bam' in f]

        for bam_file in bam_files:
            # Compare the bam's read group ID to the folder name and the file name
            bam_full_path = os.path.join(*[output_dir, folder, bam_file])
            rg_id = subprocess.check_output('samtools view -H {} | grep \"@RG\" | cut -f2'.format(bam_full_path), shell=True)
            rg_id = rg_id.split(':')[1]
            rg_id = rg_id.strip()

            logger.info(rg_id)
            logger.info(bam_full_path)
            assert rg_id in bam_full_path
            assert rg_id in folder


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-o',
        '--output_dir',
        help='Outputs folder to test',
        required=True
    )
    parser.add_argument(
        '-l',
        '--log_level',
        default='info',
        required=False
    )
    args = parser.parse_args()
    return args


def setup_logging(args):
    LEVELS = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    log_level = LEVELS[args.log_level]
    logger.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def main():
    args = parse_arguments()
    setup_logging(args)

    test_folders_have_all_correct_files(args.output_dir)
    test_rg_id_matches_sample_id(args.output_dir)

if __name__ == '__main__':
    main()
