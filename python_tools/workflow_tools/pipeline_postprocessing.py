import os
import errno
import shutil
import logging
import argparse
import pandas as pd

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
    TITLE_FILE__SAMPLE_ID_COLUMN,
    TITLE_FILE__POOL_COLUMN,
    SAMPLE_SEP_FASTQ_DELIMETER,
)

# Global variable
dry_run = False


def variables_from_title_file(title_file, project_name):
    tf = pd.read_csv(title_file, sep="\t", comment="#", header="infer")
    try:
        sample_ids = list(
            filter(lambda x: x, tf[TITLE_FILE__SAMPLE_ID_COLUMN].tolist())
        )
    except KeyError:
        raise Exception(
            "Title file does not have the required column {}".format(
                TITLE_FILE__SAMPLE_ID_COLUMN
            )
        )

    if len(sample_ids) != len(set(sample_ids)):
        raise Exception("Duplicate sampleIDs present in {}".format(title_file))

    if not project_name:
        try:
            project_name = list(
                filter(lambda x: x, tf[TITLE_FILE__POOL_COLUMN].tolist())
            )
        except KeyError:
            raise Exception(
                "Title file does not have the required column {}".format(
                    TITLE_FILE__POOL_COLUMN
                )
            )

    if not len(set(project_name)) == 1:
        raise Exception("Title file should have a single unique project/pool name")

    project_name = project_name.pop()

    # sort sample_ids by length of sample names
    sample_ids.sort(key=len)
    sample_ids.reverse()
    return sample_ids, project_name


def symlink_bams(pipeline_outputs_folder, softlink, project_name, title_file):
    """
    Create directories with symlinks to pipeline bams
    Todo: clean this function

    :param pipeline_outputs_folder: Toil outputs directory with Sample folders of collapsed bams
    :return:
    """
    sample_ids = []
    if title_file:
        sample_ids, project_name = variables_from_title_file(title_file, project_name)

    link_function = os.symlink if softlink else os.link

    for bam_search in zip(BAM_DIRS, BAM_SEARCHES):
        output_dir = os.path.join(pipeline_outputs_folder, bam_search[0])
        try:
            if not dry_run:
                os.makedirs(output_dir)
        except OSError as e:
            if e.errno == errno.EEXIST:
                print("NOTE: {} already exists!".format(output_dir))
                pass
            else:
                raise

        all_folders = [
            filename
            for filename in os.listdir(pipeline_outputs_folder)
            if os.path.isdir(os.path.join(pipeline_outputs_folder, filename))
        ]

        # Find the output folders with bams inside
        sample_folders = list(
            filter(
                lambda x: substring_in_list(".bam", listdir(pipeline_outputs_folder, x))
                and not (TMPDIR_SEARCH.match(x) or OUT_TMPDIR_SEARCH.match(x)),
                all_folders,
            )
        )

        for sample_folder in sample_folders:
            sample_folder = os.path.join(pipeline_outputs_folder, sample_folder)

            bams = list(
                filter(lambda x: bam_search[1].match(x), os.listdir(sample_folder))
            )

            for bam in bams:
                # Find sample id in the bam name
                sample_bam_boolean = [
                    os.path.basename(bam).startswith(
                        sample_id + SAMPLE_SEP_FASTQ_DELIMETER
                    )
                    for sample_id in sample_ids
                ]
                if any(sample_bam_boolean):
                    matched_id = sample_ids[sample_bam_boolean.index(True)]
                    # sample_ids.remove(matched_id)
                    new_bam = bam.replace(
                        matched_id + SAMPLE_SEP_FASTQ_DELIMETER,
                        matched_id
                        + SAMPLE_SEP_FASTQ_DELIMETER
                        + project_name
                        + SAMPLE_SEP_FASTQ_DELIMETER,
                    )
                else:
                    if title_file:
                        raise Exception(
                            "No matching sample id found in {} for {}".format(
                                title_file, bam
                            )
                        )
                    new_bam = bam

                # Link bam
                bam_source_path = os.path.abspath(os.path.join(sample_folder, bam))
                bam_target_path = os.path.abspath(os.path.join(output_dir, new_bam))

                # Todo: Give "-unfiltered" name to bam in collapsing step
                if bam_search[1].match("__aln_srt_IR_FX.bam"):
                    bam_target_path = bam_target_path.replace(".bam", "-unfiltered.bam")

                logging.info(
                    "Linking {} to {}".format(bam_source_path, bam_target_path)
                )
                if not dry_run:
                    link_function(bam_source_path, bam_target_path)

                # Link index file
                bai = bam.replace(".bam", ".bai")
                new_bai = new_bam.replace(".bam", ".bai")
                bai_source_path = os.path.abspath(os.path.join(sample_folder, bai))
                bai_target_path = os.path.abspath(os.path.join(output_dir, new_bai))

                # Todo: Give "-unfiltered" name to bam in collapsing step
                if bam_search[1].match("__aln_srt_IR_FX.bam"):
                    bai_target_path = bai_target_path.replace(".bai", "-unfiltered.bai")

                logging.info(
                    "Linking {} to {}".format(bai_source_path, bai_target_path)
                )
                if not dry_run:
                    link_function(bai_source_path, bai_target_path)


def move_trim_files(pipeline_outputs_folder):
    """
    Move all Trimgalore-related files to a single folder

    :param pipeline_outputs_folder:
    :return:
    """
    output_files = os.listdir(pipeline_outputs_folder)
    trim_files = list(filter(lambda x: TRIM_FILE_SEARCH.match(x), output_files))

    new_trim_dir = os.path.join(pipeline_outputs_folder, TRIM_FILES_DIR)

    try:
        if not dry_run:
            os.makedirs(new_trim_dir)
    except OSError as e:
        if e.errno == errno.EEXIST:
            print("NOTE: {} already exists!".format(new_trim_dir))
        else:
            raise

    logging.info("Moving {} files to trim folder".format(len(trim_files)))
    for trim_file in trim_files:
        old_loc = os.path.join(pipeline_outputs_folder, trim_file)
        if not dry_run:
            shutil.move(old_loc, new_trim_dir)


def move_markduplicates_files(pipeline_outputs_folder):
    """
    Move all MarkDuplicates-related files to a single folder

    :param pipeline_outputs_folder:
    :return:
    """
    md_files = list(
        filter(
            lambda x: MARK_DUPLICATES_FILE_SEARCH.match(x),
            os.listdir(pipeline_outputs_folder),
        )
    )
    new_md_dir = os.path.join(pipeline_outputs_folder, MARK_DUPLICATES_FILES_DIR)

    try:
        if not dry_run:
            os.makedirs(new_md_dir)
    except OSError as e:
        if e.errno == errno.EEXIST:
            print("NOTE: {} already exists!".format(new_md_dir))
        else:
            raise

    logging.info("Moving {} files to trim folder".format(len(md_files)))
    for md_file in md_files:
        old_loc = os.path.join(pipeline_outputs_folder, md_file)
        if not dry_run:
            shutil.move(old_loc, new_md_dir)


def move_covered_intervals_files(pipeline_outputs_folder):
    """
    Move all FCI-related files to a single folder

    :param pipeline_outputs_folder:
    :return:
    """
    ci_files = list(
        filter(
            lambda x: COVERED_INTERVALS_FILE_SEARCH.match(x),
            os.listdir(pipeline_outputs_folder),
        )
    )
    new_ci_dir = os.path.join(pipeline_outputs_folder, COVERED_INTERVALS_DIR)

    try:
        if not dry_run:
            os.makedirs(new_ci_dir)
    except OSError as e:
        if e.errno == errno.EEXIST:
            print("NOTE: {} already exists!".format(new_ci_dir))
        else:
            raise

    logging.info("Moving {} files to trim folder".format(len(ci_files)))
    for ci_file in ci_files:
        old_loc = os.path.join(pipeline_outputs_folder, ci_file)
        if not dry_run:
            shutil.move(old_loc, new_ci_dir)


def delete_extraneous_output_folders(pipeline_outputs_folder):
    """
    Delete Toil's tmp, tmpXXXXXX, and out_tmpdirXXXXXX directories.

    WARNING: this step will delete files. A failed workflow cannot be restarted after this action.

    :param pipeline_outputs_folder: Toil outputs directory with tempdirs to remove
    :return:
    """
    logging.warn(
        "Deleting Toil temporary files, workflow can no longer be restarted after this action."
    )
    tempdirs = list(
        filter(lambda x: TMPDIR_SEARCH.match(x), os.listdir(pipeline_outputs_folder))
    )
    tempdirs += list(
        filter(
            lambda x: OUT_TMPDIR_SEARCH.match(x), os.listdir(pipeline_outputs_folder)
        )
    )

    for tempdir in tempdirs:
        logging.info("Removing temporary directory {}".format(tempdir))
        if not dry_run:
            shutil.rmtree(os.path.join(pipeline_outputs_folder, tempdir))

    # tmpdir = filter(lambda x: TMPDIR_SEARCH_2.match(x), os.listdir(pipeline_outputs_folder))
    # assert len(tmpdir) == 1
    # if not dry_run: shutil.rmtree(os.path.join(pipeline_outputs_folder, tmpdir[0]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--log",
        dest="logLevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    parser.add_argument(
        "-s", "--softlink", action="store_true", dest="softlink", help="softlink bams"
    )
    parser.add_argument(
        "-dr",
        "--dry_run",
        action="store_true",
        dest="dry_run",
        help="Post-processing dry run",
    )
    parser.add_argument(
        "-d", "--directory", help="Toil outputs directory to be cleaned", required=True
    )
    parser.add_argument(
        "-p",
        "--project_name",
        help="Project name that you like to add to the bam file name",
    )
    parser.add_argument(
        "-t",
        "--title_file",
        help="Title file concerning the project. The file should contain all the samples in the project.",
    )
    args = parser.parse_args()

    # resolve args
    if args.dry_run:
        global dry_run
        dry_run = True
        args.logLevel = "DEBUG"
    
    if args.logLevel:
        logging.basicConfig(level=getattr(logging, args.logLevel))

    if args.project_name and not args.title_file:
        raise Exception("--title_file is required when --project_name is defined.")

    delete_extraneous_output_folders(args.directory)
    symlink_bams(args.directory, args.softlink, args.project_name, args.title_file)
    move_trim_files(args.directory)
    move_markduplicates_files(args.directory)
    move_covered_intervals_files(args.directory)


if __name__ == "__main__":
    main()
