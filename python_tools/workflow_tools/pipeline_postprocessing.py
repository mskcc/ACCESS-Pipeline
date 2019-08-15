import os
import re
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
    TOIL_LOG,
)


class AccessProject(object):
    """
    A base class to represent the directory structure of an ACCESS analysis
    directory and the associated methods for post-processing.
    """

    def __init__(self, args, logger=None):
        self._main = args.pd
        self._qc = args.qcd
        self._vc = args.vcd
        self._cnv = args.cd
        self._msi = args.md
        self._sv = args.svd
        self._dry_run = args.dry_run
        self._softlink = args.softlink
        self._title_file = args.title_file
        self._project_name = args.project_name
        self._name = args.project_name
        self._loglevel = args.logLevel
        self._ap = args.ap
        if logger:
            self._logger = logger
        else:
            self._logger = logging.getLogger("dummy").addHandler(logging.NullHandler())

    def _qc_post_processing(self):
        """
        Processing unique to a ACCESS qc directory.
        """
        self._select_bams()
        self._move_files(TRIM_FILE_SEARCH, TRIM_FILES_DIR)
        self._move_files(MARK_DUPLICATES_FILE_SEARCH, MARK_DUPLICATES_FILES_DIR)
        self._move_files(COVERED_INTERVALS_FILE_SEARCH, COVERED_INTERVALS_DIR)

    def commence_post_processing(self):
        """
        For each type of analysis directory - qc, vc, msi, cnv, sv - perform
        generic and analysis-specific post-processing.
        """
        self._parse_title_file()
        for key, val in self._get_analysis_type().items():
            self._process_dir = val
            if key == "qc":
                self._qc_post_processing()
            self._clean()
            if self._ap:
                self._miscellaneous_processing(analysis_type=key)

    # shared methods
    def _get_analysis_type(self):
        """
        Select analysis types based on the provided
        user arguments
        """
        analysis_types = {
            "qc": self._qc,
            "vc": self._vc,
            "msi": self._msi,
            "cnv": self._cnv,
            "sv": self._sv,
        }
        for key, val in analysis_types.items():
            if val is None:
                analysis_types.pop(key)
        return analysis_types

    def _make_dir(self, dirname):
        """
        Helper method to create a directory that does not throw
        an exception if the directory already exist.
        """
        try:
            if not self._dry_run:
                os.makedirs(dirname)
        except OSError as e:
            if e.errno == errno.EEXIST:
                print("NOTE: {} already exists!".format(dirname))
            else:
                raise

    def _clean(self):
        """
        Remove toil logs and extraneous intermediate tmp directories
        """
        toil_logs = list(
            filter(lambda x: TOIL_LOG.match(x), os.listdir(self._process_dir))
        )

        if not self._dry_run:
            self._logger.warn(
                "Deleting Toil temporary files, workflow can no longer be restarted after this action."
            )
        tempdirs = list(
            filter(
                lambda x: TMPDIR_SEARCH.match(x) or OUT_TMPDIR_SEARCH.match(x),
                os.listdir(self._process_dir),
            )
        )

        for tempdir in tempdirs:
            self._logger.info("Removing temporary directory {}".format(tempdir))
            if not self._dry_run:
                shutil.rmtree(os.path.join(self._process_dir, tempdir))

        for log in toil_logs:
            self._logger.info(
                "Removing log file {}".format(os.path.join(self._process_dir, log))
            )
            if not self._dry_run:
                os.remove(os.path.join(self._process_dir, log))

    def _parse_title_file(self):
        """
        Get sample names and project name from title_file
        """
        tf = pd.read_csv(self._title_file, sep="\t", comment="#", header="infer")
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
            raise Exception("Duplicate sampleIDs present in {}".format(self._title_file))

        if not self._project_name:
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
                raise Exception(
                    "Title file should have a single unique project/pool name"
                )

            self._project_name = project_name.pop()

        # sort sample_ids by length of sample names
        #  this is to ensure that in downstream steps, longest sample names are
        #  used to identify matching bam files. This will eliminate incorrect matching
        #  in the case a shorter sample name is a substring of a longer sample name.
        sample_ids.sort(key=len)
        sample_ids.reverse()
        self._sample_ids = sample_ids

    def _link_file(self, src_file, target_file, src_dir, target_dir):
        """
        Helper method to link a file form a source dir to target dir.
        """
        link_function = os.symlink if self._softlink else os.link
        src_file_path = os.path.abspath(os.path.join(src_dir, src_file))
        target_file_path = os.path.abspath(os.path.join(target_dir, target_file))

        self._logger.info("Linking {} to {}".format(src_file_path, target_file_path))
        if not self._dry_run:
            try:
                link_function(src_file_path, target_file_path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

    def _select_bams(self):
        """
        Select bams for linking based on the directory structure and 
        bam search patterns.
        """
        select_conditions = (
            lambda x: os.path.isdir(x)
            and not (
                TMPDIR_SEARCH.match(os.path.basename(x))
                or OUT_TMPDIR_SEARCH.match(os.path.basename(x))
            )
            and any([b.endswith(".bam") for b in os.listdir(x)])
        )
        dirs = list(
            filter(
                select_conditions,
                [
                    os.path.join(self._process_dir, sub_dir)
                    for sub_dir in os.listdir(self._process_dir)
                ],
            )
        )
        bams = []
        for d in dirs:
            bams.extend(
                map(
                    lambda x: os.path.join(d, x),
                    list(filter(lambda x: x.endswith(".bam"), os.listdir(d))),
                )
            )
        for bam_search in zip(BAM_DIRS, BAM_SEARCHES):
            output_dir = os.path.join(self._process_dir, bam_search[0])
            self._make_dir(output_dir)
            select_bams = map(
                lambda x: x, list(filter(lambda x: bam_search[1].match(x), bams))
            )
            self._link_grouped_bams(select_bams, output_dir)

    def _link_grouped_bams(self, bams, target_dir):
        """
        Parse and process bam file names, if applicable, before
        linking the file to target directory.
        """
        for bam in bams:
            src_dir, bam = os.path.dirname(bam), os.path.basename(bam)
            sample_bam_bool = [
                bam.startswith(sample_id + SAMPLE_SEP_FASTQ_DELIMETER)
                for sample_id in self._sample_ids
            ]
            matched_id = self._sample_ids[sample_bam_bool.index(True)]
            if matched_id:
                new_bam = bam.replace(
                    matched_id + SAMPLE_SEP_FASTQ_DELIMETER,
                    SAMPLE_SEP_FASTQ_DELIMETER.join([matched_id, self._project_name])
                    + SAMPLE_SEP_FASTQ_DELIMETER,
                )
            else:
                if self._title_file:
                    raise Exception(
                        "No matching sample id found in {} for {}".format(
                            self._title_file, bam
                        )
                    )
                new_bam = bam

            # Link bam and bai
            self._link_file(bam, new_bam, src_dir, target_dir)
            new_bai, bai = [x.replace(".bam", ".bai") for x in (new_bam, bam)]
            self._link_file(bai, new_bai, src_dir, target_dir)

    def _move_files(self, search_pattern, target_dir):
        """
        Move files, selected using search_pattern, to a target directory.
        """
        files = list(
            filter(lambda x: search_pattern.match(x), os.listdir(self._process_dir))
        )
        target_dir = os.path.join(self._process_dir, target_dir)
        self._make_dir(target_dir)

        self._logger.info("Moving {} files to {}".format(len(files), target_dir))
        for file in files:
            old_loc = os.path.join(self._process_dir, file)
            if not self._dry_run:
                shutil.move(old_loc, target_dir)

    def _miscellaneous_processing(self, mis_pros_dir="cvr_files", analysis_type="qc"):
        """
        Miscellaneous processes that are not part of the main methods.
        """

        def ccopy(src, target):
            logging.info("Copying {} to {}".format(src, target))
            if not self._dry_run:
                shutil.copy(src, target)

        target_dir = os.path.join(os.path.dirname(self._process_dir), mis_pros_dir)
        self._make_dir(target_dir)
        if analysis_type == "qc":
            ccopy(
                self._process_dir
                + "/QC_Results/aggregate_tables/qc_sample_coverage_A_targets.txt",
                target_dir + "/sample_exon_covg.txt",
            )
        if analysis_type == "msi":
            ccopy(
                self._process_dir + "/msi_results.txt", target_dir + "/msi_results.txt"
            )
        if analysis_type == "sv":
            ccopy(
                self._process_dir + "/" + self._project_name + "_AllAnnotatedSVs.txt",
                target_dir + "/annotated_structural_variants.txt",
            )
        if analysis_type == "cnv":
            ccopy(
                self._process_dir
                + "/"
                + self._project_name
                + "_copynumber_segclusp.genes.txt",
                target_dir + "/cnv_variants_gene_level.txt",
            )
            ccopy(
                self._process_dir
                + "/"
                + self._project_name
                + "_copynumber_segclusp.intragenic.txt",
                target_dir + "/cnv_intra_genic.txt",
            )
            # ccopy(self._process_dir + "/" + self._project_name + "_copynumber_segclups.probes.txt",
            # target_dir + "/probes_level_cnv.json")
        if analysis_type == "vc":
            # Create tumor normal pair file
            self._logger.info("Copying {} to {}.".format(self._process_dir + "/Title_file_to_paired.csv", target_dir + "/" + self._project_name + "_NormalUsedInMutationCalling.txt"))
            if not self._dry_run:
                normals_file = pd.read_csv(self._process_dir + "/Title_file_to_paired.csv", index_col=None, header=0, sep="\t")
                normals_file["normal_id"] = normals_file["normal_id"].replace(np.NaN, "Unmatched")
                normals_file.to_csv(target_dir + "/" + self._project_name + "_NormalUsedInMutationCalling.txt", header=False, index=None, sep="\t")
            
            # Variants passing filters
            ccopy(
                self._process_dir + "/" + self._project_name + "_ExonicFiltered.txt",
                target_dir + "/annotated_exonic_variants.txt",
            )
            ccopy(
                self._process_dir + "/" + self._project_name + "_SilentFiltered.txt",
                target_dir + "/annotated_silent_variants.txt",
            )
            ccopy(
                self._process_dir
                + "/"
                + self._project_name
                + "_NonPanelExonicFiltered.txt",
                target_dir + "/annotated_nonpanel_exonic_variants.txt",
            )
            ccopy(
                self._process_dir
                + "/"
                + self._project_name
                + "_NonPanelSilentFiltered.txt",
                target_dir + "/annotated_nonpanel_silent_variants.txt",
            )
            # Variants failing filters
            dropped_variants_files = map(
                lambda x: self._process_dir + "/" + self._project_name + x,
                [
                    "_ExonicDropped.txt",
                    "_SilentDropped.txt",
                    "_NonPanelExonicDropped.txt",
                    "_NonPanelSilentFiltered.txt",
                ],
            )
            self._logger.info(
                "Combining variants from {} to {}".format(
                    ",".join(dropped_variants_files),
                    target_dir + "/annotated_dropped_variants.txt",
                )
            )
            if not self._dry_run:
                df_from_each_file = (
                    pd.read_csv(f, index_col=None, header=0, sep="\t")
                    for f in dropped_variants_files
                )
                dropped_variants = pd.concat(df_from_each_file, ignore_index=True)
                dropped_variants.to_csv(
                    target_dir + "/annotated_dropped_variants.txt",
                    header=True,
                    index=None,
                    sep="\t",
                )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--log",
        dest="logLevel",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    parser.add_argument(
        "-s", "--softlink", action="store_true", dest="softlink", help="softlink bams"
    )
    parser.add_argument(
        "-dr", "--dry_run", action="store_true", help="Post-processing dry run"
    )
    parser.add_argument(
        "-pd",
        "--project_directory",
        action="store",
        dest="pd",
        help="Main project directory that is expected to contain Toil outputs directory from various analysis to be cleaned",
        required=False,
    )
    parser.add_argument(
        "-qcd",
        "--qc_directory",
        action="store",
        dest="qcd",
        help="QC directory that is required to be cleaned.",
        required=False,
    )
    parser.add_argument(
        "-vcd",
        "--vc_directory",
        action="store",
        dest="vcd",
        help="Variant calling directory that is required to be cleaned.",
        required=False,
    )
    parser.add_argument(
        "-md",
        "--msi_directory",
        action="store",
        dest="md",
        help="MSI directory that is required to be cleaned.",
        required=False,
    )
    parser.add_argument(
        "-svd",
        "--sv_directory",
        action="store",
        dest="svd",
        help="Structural variants directory that is required to be cleaned.",
        required=False,
    )
    parser.add_argument(
        "-cd",
        "--cv_directory",
        action="store",
        dest="cd",
        help="Copy number directory that is required to be cleaned.",
        required=False,
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
        required=True,
    )
    parser.add_argument(
        "-ap",
        "--additional_processing",
        dest="ap",
        action="store_true",
        help="Perform additional user defined post-processing that is not required for the main pipeline",
        required=False,
    )
    args = parser.parse_args()

    # resolve args
    if args.dry_run:
        args.logLevel = "DEBUG"

    logging.basicConfig(level=getattr(logging, args.logLevel))
    logger = logging.getLogger("Post_Proccessing")

    if not any([args.pd, args.qcd, args.vcd, args.md, args.svd, args.cd]):
        raise Exception(
            "At least one of the following parameters must be supplied with an argument: --project_directory, --qc_directory, --msi_directory, --sv_directory, --cv_directory"
        )

    # Start post-processing
    if args.pd:
        print(
            "Main project directory is defined. Project level post-processing is assumed."
        )
        expected_subdir = [
            "processed_data",
            "Variant_Calls",
            "MSI",
            "Structural_Variants",
            "CNV",
        ]
        arg_attributes = ["qcd", "vcd", "md", "svd", "cd"]
        # if sub-directories are not defined, use expected sub-directory names
        #  and raise excpetion if they are missing.
        for index, attribute in enumerate(arg_attributes):
            if getattr(args, attribute) is None:
                setattr(args, attribute, os.path.join(args.pd, expected_subdir[index]))

            if not os.path.isdir(getattr(args, attribute)):
                raise OSError(
                    "No such file or directory: '{}'".format(getattr(args, attribute))
                )

    project = AccessProject(args, logger)
    project.commence_post_processing()


if __name__ == "__main__":
    main()
