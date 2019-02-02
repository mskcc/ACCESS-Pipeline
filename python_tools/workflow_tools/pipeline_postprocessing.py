import os
import shutil
import logging
import argparse

from python_tools.util import substring_in_list, listdir
from python_tools.constants import (
    BAM_DIRS,
    BAM_SEARCHES,
    TRIM_FILE_SEARCH,
    TRIM_FILES_DIR,
    MARK_DUPLICATES_FILE_SEARCH,
    MARK_DUPLICATES_FILES_DIR,
    COVERED_INTERVALS_FILE_SEARCH,
    COVERED_INTERVALS_DIR,
    TMPDIR_SEARCH,
    OUT_TMPDIR_SEARCH,
    TMPDIR_SEARCH_2
)


def symlink_bams(pipeline_outputs_folder):
    '''
    Create directories with symlinks to pipeline bams
    Todo: clean this function

    :param pipeline_outputs_folder: Toil outputs directory with Sample folders of collapsed bams
    :return:
    '''
    for bam_search in zip(BAM_DIRS, BAM_SEARCHES):
        output_dir = os.path.join(pipeline_outputs_folder, bam_search[0])
        os.makedirs(output_dir)

        all_folders = [filename for filename in os.listdir(pipeline_outputs_folder) if
                   os.path.isdir(os.path.join(pipeline_outputs_folder, filename))]

        # Find the output folders with bams inside
        sample_folders = filter(lambda x: substring_in_list('.bam', listdir(pipeline_outputs_folder, x)), all_folders)

        for sample_folder in sample_folders:
            sample_folder = os.path.join(pipeline_outputs_folder, sample_folder)

            bams = filter(lambda x: bam_search[1].match(x), os.listdir(sample_folder))

            for bam in bams:
                # Link bam
                bam_source_path = os.path.abspath(os.path.join(sample_folder, bam))
                bam_target_path = os.path.abspath(os.path.join(output_dir, bam))

                # Todo: Give "-unfiltered" name to bam in collapsing step
                if bam_search[1].match('__aln_srt_IR_FX.bam'):
                    bam_target_path = bam_target_path.replace('.bam', '-unfiltered.bam')

                logging.info('Linking {} to {}'.format(bam_source_path, bam_target_path))
                os.link(bam_source_path, bam_target_path)

                # Link index file
                bai = bam.replace('.bam', '.bai')
                bai_source_path = os.path.abspath(os.path.join(sample_folder, bai))
                bai_target_path = os.path.abspath(os.path.join(output_dir, bai))

                # Todo: Give "-unfiltered" name to bam in collapsing step
                if bam_search[1].match('__aln_srt_IR_FX.bam'):
                    bai_target_path = bai_target_path.replace('.bai', '-unfiltered.bai')

                logging.info('Linking {} to {}'.format(bai_source_path, bai_target_path))
                os.link(bai_source_path, bai_target_path)


def move_trim_files(pipeline_outputs_folder):
    """
    Move all Trimgalore-related files to a single folder

    :param pipeline_outputs_folder:
    :return:
    """
    output_files = os.listdir(pipeline_outputs_folder)
    trim_files = filter(lambda x: TRIM_FILE_SEARCH.match(x), output_files)

    new_trim_dir = os.path.join(pipeline_outputs_folder, TRIM_FILES_DIR)

    if not os.path.exists(new_trim_dir):
        os.makedirs(new_trim_dir)

    logging.info('Moving {} files to trim folder'.format(len(trim_files)))
    for trim_file in trim_files:
        old_loc = os.path.join(pipeline_outputs_folder, trim_file)
        shutil.move(old_loc, new_trim_dir)


def move_markduplicates_files(pipeline_outputs_folder):
    """
    Move all MarkDuplicates-related files to a single folder

    :param pipeline_outputs_folder:
    :return:
    """
    md_files = filter(lambda x: MARK_DUPLICATES_FILE_SEARCH.match(x), os.listdir(pipeline_outputs_folder))
    new_md_dir = os.path.join(pipeline_outputs_folder, MARK_DUPLICATES_FILES_DIR)

    if not os.path.exists(new_md_dir):
        os.makedirs(new_md_dir)

    logging.info('Moving {} files to trim folder'.format(len(md_files)))
    for md_file in md_files:
        old_loc = os.path.join(pipeline_outputs_folder, md_file)
        shutil.move(old_loc, new_md_dir)


def move_covered_intervals_files(pipeline_outputs_folder):
    """
    Move all FCI-related files to a single folder

    :param pipeline_outputs_folder:
    :return:
    """
    ci_files = filter(lambda x: COVERED_INTERVALS_FILE_SEARCH.match(x), os.listdir(pipeline_outputs_folder))
    new_ci_dir = os.path.join(pipeline_outputs_folder, COVERED_INTERVALS_DIR)

    if not os.path.exists(new_ci_dir):
        os.makedirs(new_ci_dir)

    logging.info('Moving {} files to trim folder'.format(len(ci_files)))
    for ci_file in ci_files:
        old_loc = os.path.join(pipeline_outputs_folder, ci_file)
        shutil.move(old_loc, new_ci_dir)


def delete_extraneous_output_folders(pipeline_outputs_folder):
    '''
    Delete Toil's tmp, tmpXXXXXX, and out_tmpdirXXXXXX directories.

    WARNING: this step will delete files. A failed workflow cannot be restarted after this action.

    :param pipeline_outputs_folder: Toil outputs directory with tempdirs to remove
    :return:
    '''
    logging.warn('Deleting Toil temporary files, workflow can no longer be restarted after this action.')
    tempdirs = filter(lambda x: TMPDIR_SEARCH.match(x), os.listdir(pipeline_outputs_folder))
    tempdirs += filter(lambda x: OUT_TMPDIR_SEARCH.match(x), os.listdir(pipeline_outputs_folder))

    for tempdir in tempdirs:
        logging.info('Removing temporary directory {}'.format(tempdir))
        shutil.rmtree(os.path.join(pipeline_outputs_folder, tempdir))

    tmpdir = filter(lambda x: TMPDIR_SEARCH_2.match(x), os.listdir(pipeline_outputs_folder))
    assert len(tmpdir) == 1
    shutil.rmtree(os.path.join(pipeline_outputs_folder, tmpdir[0]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the logging level")
    parser.add_argument("-d", "--directory", help="Toil outputs directory to be cleaned", required=True)
    args = parser.parse_args()

    if args.logLevel:
        logging.basicConfig(level=getattr(logging, args.logLevel))

    delete_extraneous_output_folders(args.directory)
    symlink_bams(args.directory)
    move_trim_files(args.directory)
    move_markduplicates_files(args.directory)
    move_covered_intervals_files(args.directory)


if __name__ == '__main__':
    main()
