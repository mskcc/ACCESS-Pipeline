import os
import shutil
import logging
import argparse

# Todo: use explicit imports (enums?)
from ..util import *


def symlink_bams(pipeline_outputs_folder):
    '''
    Create directories with symlinks to pipeline bams
    Todo: clean this function

    :param pipeline_outputs_folder: Toil outputs directory with Sample folders of collapsed bams
    :return:
    '''
    for collapsed_folder in filter(lambda x: 'Sample' in x, os.listdir(pipeline_outputs_folder)):
        collapsed_folder = os.path.join(pipeline_outputs_folder, collapsed_folder)

        for bam_search in zip(BAM_DIRS, BAM_SEARCHES):
            output_dir = os.path.join(pipeline_outputs_folder, bam_search[0])
            os.makedirs(output_dir)

            bams = filter(lambda x: bam_search[1] in x, os.listdir(collapsed_folder))

            for bam in bams:
                # Link bam
                bam_source_path = os.path.abspath(os.path.join(collapsed_folder, bam))
                bam_target_path = os.path.abspath(os.path.join(output_dir, bam))

                # Todo: Give "-unfiltered" name to bam in collapsing step
                if bam_search[1] == UNFILTERED_BAM_SEARCH:
                    bam_target_path = bam_target_path.replace('.bam', '-unfiltered.bam')

                logging.info('Linking {} to {}'.format(bam_source_path, bam_target_path))
                os.symlink(bam_source_path, bam_target_path)

                # Link index file
                bai = bam.replace('.bam', '.bai')
                bai_source_path = os.path.abspath(os.path.join(collapsed_folder, bai))
                bai_target_path = os.path.abspath(os.path.join(output_dir, bai))

                # Todo: Give "-unfiltered" name to bam in collapsing step
                if bam_search[1] == UNFILTERED_BAM_SEARCH:
                    bai_target_path = bai_target_path.replace('.bai', '-unfiltered.bai')

                logging.info('Linking {} to {}'.format(bai_source_path, bai_target_path))
                os.symlink(bai_source_path, bai_target_path)


def delete_extraneous_output_folders(pipeline_outputs_folder):
    '''
    Delete tmpXXXXXX and out_tmpdirXXXXXX directories

    :param pipeline_outputs_folder: Toil outputs directory with tempdirs to remove
    :return:
    '''
    tempdirs = filter(lambda x: TMPDIR_SEARCH.match(x), os.listdir(pipeline_outputs_folder))
    tempdirs += filter(lambda x: OUT_TMPDIR_SEARCH.match(x), os.listdir(pipeline_outputs_folder))

    for tempdir in tempdirs:
        logging.info('Removing temporary directory {}'.format(tempdir))
        shutil.rmtree(os.path.join(pipeline_outputs_folder, tempdir))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", help="Toil outputs directory to be cleaned", required=True)
    args = parser.parse_args()

    symlink_bams(args.directory)
    delete_extraneous_output_folders(args.directory)


if __name__ == '__main__':
    main()
