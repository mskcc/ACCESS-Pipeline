import os
import re
from collections import OrderedDict

from python_tools.root import ROOT_DIR

#############
# Resources #
#############
RESOURCES_FOLDER = os.path.join(ROOT_DIR, "resources")

RUN_FILES_FOLDER = os.path.join(RESOURCES_FOLDER, "run_files")
RUN_PARAMS_FOLDER = os.path.join(RESOURCES_FOLDER, "run_params")
RUN_TOOLS_FOLDER = os.path.join(RESOURCES_FOLDER, "run_tools")

TEST = "test.yaml"
LOCAL = "local.yaml"
PRODUCTION = "production.yaml"

# Run Files
RUN_FILES = os.path.join(RUN_FILES_FOLDER, PRODUCTION)
RUN_FILES_TEST = os.path.join(RUN_FILES_FOLDER, TEST)
RUN_FILES_LOCAL = os.path.join(RUN_FILES_FOLDER, LOCAL)

# Run Parameters
RUN_PARAMS = os.path.join(RUN_PARAMS_FOLDER, PRODUCTION)
RUN_PARAMS_TEST = os.path.join(RUN_PARAMS_FOLDER, TEST)

# Resource Paths
TOOL_RESOURCES_LOCAL                = os.path.join(ROOT_DIR, 'resources/run_tools/local.yaml')
TOOL_RESOURCES_PROD                 = os.path.join(ROOT_DIR, 'resources/run_tools/phoenix.yaml')
TOOL_RESOURCES_LUNA                 = os.path.join(ROOT_DIR, 'resources/run_tools/luna.yaml')
ACCESS_VARIANTS_RUN_TOOLS_MANTA     = os.path.join(RUN_TOOLS_FOLDER, 'SV.yaml')

# ACCESS-Variants Resources
ACCESS_VARIANTS_RUN_FILES_PATH = os.path.join(RUN_FILES_FOLDER, 'ACCESS_variants_run_files.yaml')
ACCESS_VARIANTS_RUN_PARAMS_PATH = os.path.join(RUN_PARAMS_FOLDER, 'ACCESS_variants_run_params.yaml')
ACCESS_VARIANTS_RUN_TOOLS_PATH = os.path.join(RUN_TOOLS_FOLDER, 'ACCESS_variants_phoenix.yaml')
ACCESS_VARIANTS_RUN_PARAMS_DELLY_PATH = os.path.join(RUN_PARAMS_FOLDER, 'ACCESS_variants_run_params_delly.yaml')

RUN_PARAMS__STANDARD_BAM_TO_COLLAPSED_QC = os.path.join(RUN_PARAMS_FOLDER, 'standard_bams_to_collapsed_qc.yaml')


##################################
# SampleSheet Column Definitions #
##################################
SAMPLE_SHEET__LANE_COLUMN = "Lane"
SAMPLE_SHEET__SAMPLE_ID_COLUMN = "Sample_ID"
SAMPLE_SHEET__PATIENT_ID_COLUMN = "Sample_Name"
SAMPLE_SHEET__BARCODE_ID1_COLUMN = "I7_Index_ID"
SAMPLE_SHEET__BARCODE_INDEX_1_COLUMN = "index"
SAMPLE_SHEET__BARCODE_ID2_COLUMN = "I5_Index_ID"
SAMPLE_SHEET__BARCODE_INDEX_2_COLUMN = "index2"
SAMPLE_SHEET__CLASS_COLUMN = "Description"
SAMPLE_SHEET__METADATA_COLUMN = "Operator"
SAMPLE_SHEET__PROJECT_ID_COLUMN = "Sample_Project"


################################
# TitleFile Column Definitions #
################################

# Columns explicity provided in sample sheet
TITLE_FILE__POOL_COLUMN = "Pool"
TITLE_FILE__SAMPLE_ID_COLUMN = "Sample"
TITLE_FILE__PATIENT_ID_COLUMN = "Patient_ID"
TITLE_FILE__SAMPLE_CLASS_COLUMN = "Class"
TITLE_FILE__BARCODE_INDEX_1_COLUMN = "Barcode_index_1"
TITLE_FILE__BARCODE_INDEX_2_COLUMN = "Barcode_index_2"
TITLE_FILE__LANE_COLUMN = "Lane"

# Columns inferred from other columns defined above
TITLE_FILE__SAMPLE_TYPE_COLUMN = "Sample_type"
TITLE_FILE__BAIT_VERSION_COLUMN = "Bait_version"

# Columns defined as constants
TITLE_FILE__COLLAB_ID_COLUMN = "Collab_ID"

# Columns inteferred from samplesheet metadata/operator column
TITLE_FILE__SEX_COLUMN = "Sex"
TITLE_FILE__PATIENT_NAME_COLUMN = "PatientName"
TITLE_FILE__ACCESSION_COLUMN = "AccessionID"
TITLE_FILE__SEQUENCER_COLUMN = "Sequencer"

# TODO:
# Columns currently filled with dummy values until DMS/LIMS figures out a way.
TITLE_FILE__POOL_INPUT_COLUMN = "Pool_input"

# Columns not current used
TITLE_FILE__BARCODE_ID_COLUMN = "Barcode"
TITLE_FILE__INPUT_NG_COLUMN = "Input_ng"
TITLE_FILE__LIBRARY_YIELD_COLUMN = "Library_yield"
TITLE_FILE__DNA_YIELD_COLUMN = "Extracted_DNA_Yield"


##########################
# Map Column Definitions #
##########################

# Map SAMPLESHEET --> TITLE_FILE
# Use OrderedDict to keep ordering for keys() and values()
columns_map_samplesheet = OrderedDict(
    [
        (SAMPLE_SHEET__PROJECT_ID_COLUMN, TITLE_FILE__POOL_COLUMN),
        (SAMPLE_SHEET__SAMPLE_ID_COLUMN, TITLE_FILE__SAMPLE_ID_COLUMN),
        (SAMPLE_SHEET__PATIENT_ID_COLUMN, TITLE_FILE__PATIENT_ID_COLUMN),
        (SAMPLE_SHEET__CLASS_COLUMN, TITLE_FILE__SAMPLE_CLASS_COLUMN),
        (SAMPLE_SHEET__BARCODE_INDEX_1_COLUMN, TITLE_FILE__BARCODE_INDEX_1_COLUMN),
        (SAMPLE_SHEET__BARCODE_INDEX_2_COLUMN, TITLE_FILE__BARCODE_INDEX_2_COLUMN),
        (SAMPLE_SHEET__LANE_COLUMN, TITLE_FILE__LANE_COLUMN),
    ]
)


###################################
# Title file generation constants #
###################################
COLLAB_ID = "DMP"
PLASMA = "plasma"
BUFFY = "buffy"
SAMPLE_ID_ALLOWED_DELIMETER = "-"
DISALLOWED_SAMPLE_ID_CHARACTERS = "!\"#$%&'()*+,./:;<=>?@[\\]^_`{|}~"
METADATA_COLUMN_DELIMETER = "|"
METADATA_REQUIRED_COLUMNS = [1, 2, 3, 4]
SELECT_SPLIT_COLUMN = [1]
ALLOWED_SAMPLE_TYPE = re.compile(r"(^TP|^TB|^NP|^NB)")
ALLOWED_SAMPLE_TYPE_LIST = ["TB", "NB", "TP", "NP"]
PLASMA_SAMPLE_TYPE = re.compile(r"(^TP|^NP)")
# PLASMA_SAMPLE_TYPE = ["TP", "NP", "T"]
BUFFY_SAMPLE_TYPE = re.compile(r"(^TB|^NB)")
# BUFFY_SAMPLE_TYPE = ["TB", "NB", "N"]
ALLOWED_SAMPLE_DESCRIPTION = ["Tumor", "Normal", "PoolTumor", "PoolNormal"]
ALLOWED_SEX = ["Male", "Female", "Control"]
ALLOWED_SEQUENCERS = ["HISEQ", "NOVASEQ"]
EXPECTED_BAIT_VERSION = "v1"
ASSAY_NAME = "ACCESS"
PROJECT_NAME = re.compile("^" + ASSAY_NAME + "v[0-9]-[A-Za-z]+-[0-9]{8}.*")
BAIT_SEARCH = re.compile("^" + ASSAY_NAME + "v[0-9]")
MERGED_LANE_VALUE = "0"

SAMPLE_SHEET_REQUIRED_COLUMNS = [
    "Lane",
    "Sample_ID",
    "Sample_Name",
    "I7_Index_ID",
    "index",
    "I5_Index_ID",
    "index2",
    "Description",
    "Control",
    "Operator",
    "Sample_Project",
]

SAMPLE_SHEET_OPTIONAL_COLUMNS = [
    "FCID",
    "Sample_Plate",
    "Sample_Well",
    "Sample_Ref",
    "Control",
    "Recipe",
]

TITLE_FILE__COLUMN_ORDER = [
    TITLE_FILE__BARCODE_ID_COLUMN,
    TITLE_FILE__POOL_COLUMN,
    TITLE_FILE__SAMPLE_ID_COLUMN,
    TITLE_FILE__COLLAB_ID_COLUMN,
    TITLE_FILE__PATIENT_ID_COLUMN,
    TITLE_FILE__SAMPLE_CLASS_COLUMN,
    TITLE_FILE__SAMPLE_TYPE_COLUMN,
    TITLE_FILE__POOL_INPUT_COLUMN,
    TITLE_FILE__BAIT_VERSION_COLUMN,
    TITLE_FILE__SEX_COLUMN,
    TITLE_FILE__PATIENT_NAME_COLUMN,
    TITLE_FILE__ACCESSION_COLUMN,
    TITLE_FILE__BARCODE_INDEX_1_COLUMN,
    TITLE_FILE__BARCODE_INDEX_2_COLUMN,
    # TITLE_FILE__LANE_COLUMN Do not include the lane column for now
]

##############################
# Pipeline Kickoff Constants #
##############################

NON_REVERSE_COMPLEMENTED = 0
REVERSE_COMPLEMENTED = 1

# Delimiter for printing logs
DELIMITER = "\n" + "*" * 20 + "\n"
# Delimiter for inputs file sections
INPUTS_FILE_DELIMITER = "\n\n" + "# " + "--" * 30 + "\n\n"

# Template identifier string that will get replaced with the project root location
PIPELINE_ROOT_PLACEHOLDER = "$PIPELINE_ROOT"

BAM_REGEX = re.compile(r".*\.bam$")

SAMPLE_SEP_FASTQ_DELIMETER = "_"
SAMPLE_SEP_DIR_DELIMETER = "/"


##########################
# Constants for QC files #
##########################

# Avoid division by zero errors
EPSILON = 1e-9

# Shorter reference to sample ID column, to be used everywhere
SAMPLE_ID_COLUMN = TITLE_FILE__SAMPLE_ID_COLUMN

# WALTZ Metrics Files Constants

# File suffixes
WALTZ_READ_COUNTS_FILENAME_SUFFIX = ".read-counts"
WALTZ_FRAGMENT_SIZES_FILENAME_SUFFIX = ".fragment-sizes"
WALTZ_INTERVALS_FILENAME_SUFFIX = "-intervals.txt"
WALTZ_INTERVALS_WITHOUT_DUPLICATES_FILENAME_SUFFIX = "-intervals-without-duplicates.txt"

TOTAL_OFF_TARGET_FRACTION_COLUMN = "total_off_target_fraction"

WALTZ_CHROMOSOME_COLUMN = "chromosome"
WALTZ_START_COLUMN = "start"
WALTZ_STOP_COLUMN = "stop"
WALTZ_INTERVAL_NAME_COLUMN = "interval_name"
WALTZ_FRAGMENT_SIZE_COLUMN = "fragment_size"
WALTZ_PEAK_COVERAGE_COLUMN = "peak_coverage"
WALTZ_AVERAGE_COVERAGE_COLUMN = "TotalCoverage"
WALTZ_GC_CONTENT_COLUMN = "gc"

# todo
WALTZ_INTERVALS_FILE_HEADER = [
    WALTZ_CHROMOSOME_COLUMN,
    WALTZ_START_COLUMN,
    WALTZ_STOP_COLUMN,
    WALTZ_INTERVAL_NAME_COLUMN,
    WALTZ_FRAGMENT_SIZE_COLUMN,
    WALTZ_PEAK_COVERAGE_COLUMN,
    WALTZ_AVERAGE_COVERAGE_COLUMN,
    WALTZ_GC_CONTENT_COLUMN,
]

WALTZ_COVERAGE_FILE_HEADER = ["TotalCoverage", "UniqueCoverage"]


# AGBM Metrics Files Constants
#
# Column names
AGBM_COVERAGE_FILENAME = "waltz-coverage.txt"
AGBM_READ_COUNTS_FILENAME = "read-counts.txt"
AGBM_FRAGMENT_SIZES_FILENAME = "fragment-sizes.txt"
AGBM_INTERVALS_COVERAGE_SUM_FILENAME = "intervals_coverage_sum.txt"


# fragment-sizes.txt
FRAGMENT_SIZE_COLUMN = "FragmentSize"
TOTAL_FREQUENCY_COLUMN = "TotalFrequency"
UNIQUE_FREQUENCY_COLUMN = "UniqueFrequency"

# read-counts.txt
TOTAL_MAPPED_COLUMN = "TotalMapped"
UNIQUE_MAPPED_COLUMN = "UniqueMapped"
TOTAL_READS_COLUMN = "TotalReads"
UNMAPPED_READS_COLUMN = "UnmappedReads"
DUPLICATE_FRACTION_COLUMN = "DuplicateFraction"
TOTAL_ON_TARGET_COLUMN = "TotalOnTarget"
UNIQUE_ON_TARGET_COLUMN = "UniqueOnTarget"
TOTAL_ON_TARGET_FRACTION_COLUMN = "TotalOnTargetFraction"
UNIQUE_ON_TARGET_FRACTION_COLUMN = "UniqueOnTargetFraction"

# File Headers
AGBM_READ_COUNTS_HEADER = [
    SAMPLE_ID_COLUMN,
    "bam",
    TOTAL_READS_COLUMN,
    UNMAPPED_READS_COLUMN,
    TOTAL_MAPPED_COLUMN,
    UNIQUE_MAPPED_COLUMN,
    DUPLICATE_FRACTION_COLUMN,
    TOTAL_ON_TARGET_COLUMN,
    UNIQUE_ON_TARGET_COLUMN,
    TOTAL_ON_TARGET_FRACTION_COLUMN,
    UNIQUE_ON_TARGET_FRACTION_COLUMN,
]

AGBM_FRAGMENT_SIZES_FILE_HEADER = [
    SAMPLE_ID_COLUMN,
    FRAGMENT_SIZE_COLUMN,
    TOTAL_FREQUENCY_COLUMN,
    UNIQUE_FREQUENCY_COLUMN,
]

# Chr\tStart\tEnd\tIntervalName\tLength\tGC\tCoverage\tCoverageWithoutDuplicates
# intervals-coverage-sum.txt
CHROMOSOME_COLUMN = "Chr"
START_COLUMN = "Start"
END_COLUMN = "End"
INTERVAL_NAME_COLUMN = "IntervalName"
LENGTH_COLUMN = "Length"
GC_COLUMN = "GC"
COVERAGE_COLUMN = "Coverage"
COVERAGE_WITH_DUPLICATES_COLUMN = "CoverageWithoutDuplicates"

AGBM_INTERVALS_COVERAGE_SUM_FILE_HEADER = [
    SAMPLE_ID_COLUMN,
    CHROMOSOME_COLUMN,
    START_COLUMN,
    END_COLUMN,
    INTERVAL_NAME_COLUMN,
    LENGTH_COLUMN,
    GC_COLUMN,
    COVERAGE_COLUMN,
    COVERAGE_WITH_DUPLICATES_COLUMN,
]

AGBM_TOTAL_AVERAGE_COVERAGE_COLUMN = "TotalCoverage"
AGBM_UNIQUE_AVERAGE_COVERAGE_COLUMN = "UniqueCoverage"

AGBM_COVERAGE_HEADER = [
    SAMPLE_ID_COLUMN,
    AGBM_TOTAL_AVERAGE_COVERAGE_COLUMN,
    AGBM_UNIQUE_AVERAGE_COVERAGE_COLUMN,
]


# TABLES MODULE Files Constants
#
# Labels for collapsing methods
TOTAL_LABEL = "TotalCoverage"
PICARD_LABEL = "Picard Unique"
MAPPED_LABEL = "Mapped"

POOL_A_LABEL = "A Targets"
POOL_B_LABEL = "B Targets"

UNFILTERED_COLLAPSING_METHOD = 'All Unique'
SIMPLEX_COLLAPSING_METHOD = 'Simplex'
DUPLEX_COLLAPSING_METHOD = 'Duplex'
SIMPLEX_DUPLEX_COMBINED = 'SimplexDuplex'

# Headers for tables
DUPLICATION_RATES_HEADER = [SAMPLE_ID_COLUMN, 'method', 'duplication_rate', 'pool']

GC_BIN_COLUMN = 'gc_bin'
METHOD_COLUMN = 'method'
GC_BIAS_HEADER = [SAMPLE_ID_COLUMN, 'interval_name', WALTZ_PEAK_COVERAGE_COLUMN, 'gc', 'method']
GC_BIAS_AVERAGE_COVERAGE_ALL_SAMPLES_HEADER = [METHOD_COLUMN, GC_BIN_COLUMN, 'coverage']
GC_BIAS_AVERAGE_COVERAGE_EACH_SAMPLE_HEADER = [METHOD_COLUMN, SAMPLE_ID_COLUMN, GC_BIN_COLUMN, 'coverage']

# Output file names
read_counts_filename = 'read_counts_agg.txt'
coverage_agg_filename = 'coverage_agg.txt'
gc_avg_each_sample_coverage_filename = 'GC_bias_with_coverage_averages_over_each_sample.txt'
gc_bias_with_coverage_filename = 'GC_bias_with_coverage.txt'
read_counts_total_filename = 'read_counts_total.txt'
coverage_per_interval_filename = 'coverage_per_interval.txt'
read_counts_table_exon_level_filename = 'read_counts_agg_exon_level.txt'
coverage_table_exon_level_filename = 'coverage_agg_exon_level.txt'
gc_cov_int_table_exon_level_filename = 'GC_bias_with_coverage_exon_level.txt'
gc_avg_each_sample_coverage_exon_level_filename = 'GC_bias_with_coverage_averages_over_each_sample_exon_level.txt'
average_coverage_across_exon_targets_filename = 'average_coverage_across_exon_targets_duplex_A.txt'

INSERT_SIZE_PREFIX = 'insert_sizes_'
INSERT_SIZE_OUTPUT_FILE_NAMES = [
    'standard_A_targets.txt',
    'unfiltered_A_targets.txt',
    'simplex_A_targets.txt',
    'duplex_A_targets.txt',
    'standard_B_targets.txt',
    'unfiltered_B_targets.txt',
    'simplex_B_targets.txt',
    'duplex_B_targets.txt',
]

EXON_COVERAGE_OUTPUT_FILE_NAMES = [
    'coverage_per_interval_A_targets_All_Unique.txt',
    'coverage_per_interval_A_targets_Duplex.txt',
    'coverage_per_interval_A_targets_Simplex.txt',
    'coverage_per_interval_A_targets_TotalCoverage.txt',
]

INSERT_SIZE_OUTPUT_FILE_NAMES = [INSERT_SIZE_PREFIX + o for o in INSERT_SIZE_OUTPUT_FILE_NAMES]

ALL_TABLES_MODULE_OUTPUT_FILES = [
    read_counts_filename,
    coverage_agg_filename,
    gc_avg_each_sample_coverage_filename,
    gc_bias_with_coverage_filename,
    read_counts_total_filename,
    coverage_per_interval_filename,
    read_counts_table_exon_level_filename,
    coverage_table_exon_level_filename,
    gc_cov_int_table_exon_level_filename,
    gc_avg_each_sample_coverage_exon_level_filename,
    average_coverage_across_exon_targets_filename
] + EXON_COVERAGE_OUTPUT_FILE_NAMES + \
INSERT_SIZE_OUTPUT_FILE_NAMES + [
    'qc_sample_coverage_A_targets.txt',
    'qc_sample_coverage_B_targets.txt'
]


####################
# Constants for VC #
####################

TUMOR_ID = 'tumor_id'
NORMAL_ID = 'normal_id'
SAMPLE_CLASS = 'class'
GROUP_BY_ID = 'Patient_ID'
SAMPLE_PAIR1 = 'Sample_x'
SAMPLE_PAIR2 = 'Sample_y'
CLASS_PAIR1 = 'Class_x'
CLASS_PAIR2 = 'Class_y'
SAMPLE_TYPE_PAIR1 = 'Sample_type_x'
SAMPLE_TYPE_PAIR2 = 'Sample_type_y'
TUMOR_CLASS = 'Tumor'
NORMAL_CLASS = 'Normal'
SAMPLE_TYPE_PLASMA = 'Plasma'
SAMPLE_TYPE_NORMAL_NONPLASMA = 'Buffycoat'
TITLE_FILE_TO_PAIRED_FILE = "Title_file_to_paired.csv"


#########
# Noise #
#########

NOISE_HEADER = [
    SAMPLE_ID_COLUMN,
    "GenotypeCount",
    "AltCount",
    "AltPercent",
    "ContributingSites",
    "Method",
]


########################
# Cleanup Outputs Step #
########################

TMPDIR_SEARCH = re.compile(r"(^tmp$|^tmp......$)")
OUT_TMPDIR_SEARCH = re.compile(r"^out_tmpdir......$")

STANDARD_BAM_DIR = "standard_bams"
UNFILTERED_BAM_DIR = "unfiltered_bams"
SIMPLEX_BAM_DIR = "simplex_bams"
DUPLEX_BAM_DIR = "duplex_bams"
TRIM_FILES_DIR = "trimming_results"
MARK_DUPLICATES_FILES_DIR = "mark_duplicates_results"
COVERED_INTERVALS_DIR = "covered_intervals_results"

BAM_FILE_REGEX = re.compile(r"\.bam$")
STANDARD_BAM_SEARCH = re.compile(r"^.*_cl_aln_srt_MD_IR_FX_BR.bam$")
UNFILTERED_BAM_SEARCH = re.compile(r"^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX.bam$")
SIMPLEX_BAM_SEARCH = re.compile(
    r"^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-simplex.bam$"
)
DUPLEX_BAM_SEARCH = re.compile(r"^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-duplex.bam$")
STANDARD_BAI_SEARCH = re.compile(r"^.*_cl_aln_srt_MD_IR_FX_BR.bai$")
UNFILTERED_BAI_SEARCH = re.compile(r"^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX.bai$")
SIMPLEX_BAI_SEARCH = re.compile(
    r"^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-simplex.bai$"
)
DUPLEX_BAI_SEARCH = re.compile(r"^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-duplex.bai$")

TRIM_FILE_SEARCH = re.compile(r"^.*_cl\.stats$")
MARK_DUPLICATES_FILE_SEARCH = re.compile(r"^.*\.md_metrics$")
COVERED_INTERVALS_FILE_SEARCH = re.compile(r"^.*(\.fci\.bed\.srt|\.fci\.list)$")

BAM_DIRS = [STANDARD_BAM_DIR, UNFILTERED_BAM_DIR, SIMPLEX_BAM_DIR, DUPLEX_BAM_DIR]

BAM_SEARCHES = [
    STANDARD_BAM_SEARCH,
    UNFILTERED_BAM_SEARCH,
    SIMPLEX_BAM_SEARCH,
    DUPLEX_BAM_SEARCH,
]
