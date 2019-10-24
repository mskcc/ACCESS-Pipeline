import os
import re
from collections import OrderedDict

# Repository main directory
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

#############
# Resources #
#############

RESOURCES_FOLDER                    = os.path.join(ROOT_DIR, 'resources')

RUN_FILES_FOLDER                    = os.path.join(RESOURCES_FOLDER, 'run_files')
RUN_PARAMS_FOLDER                   = os.path.join(RESOURCES_FOLDER, 'run_params')
RUN_TOOLS_FOLDER                    = os.path.join(RESOURCES_FOLDER, 'run_tools')

TEST                                = 'test.yaml'
LOCAL                               = 'local.yaml'
PRODUCTION                          = 'production.yaml'

# Run Files
RUN_FILES                           = os.path.join(RUN_FILES_FOLDER, PRODUCTION)
RUN_FILES_TEST                      = os.path.join(RUN_FILES_FOLDER, TEST)
RUN_FILES_LOCAL                     = os.path.join(RUN_FILES_FOLDER, LOCAL)

# Run Parameters
RUN_PARAMS                          = os.path.join(RUN_PARAMS_FOLDER, PRODUCTION)
RUN_PARAMS_TEST                     = os.path.join(RUN_PARAMS_FOLDER, TEST)

# Luna Resource Paths
TOOL_RESOURCES_LOCAL                = os.path.join(ROOT_DIR, 'resources/run_tools/local.yaml')
TOOL_RESOURCES_PROD                 = os.path.join(ROOT_DIR, 'resources/run_tools/phoenix.yaml')

RUN_PARAMS__STANDARD_BAM_TO_COLLAPSED_QC = os.path.join(RUN_PARAMS_FOLDER, 'standard_bams_to_collapsed_qc.yaml')



###############################
# Manifest Column Definitions #
###############################

MANIFEST__BARCODE_ID_COLUMN                 = 'BARCODE_ID'
# Todo: use "P5", "P7"
MANIFEST__BARCODE_INDEX_1_COLUMN            = 'BARCODE_INDEX_1'
MANIFEST__BARCODE_INDEX_2_COLUMN            = 'BARCODE_INDEX_2'
MANIFEST__CAPTURE_NAME_COLUMN               = 'CAPTURE_NAME'
MANIFEST__CMO_SAMPLE_ID_COLUMN              = 'CMO_SAMPLE_ID'
MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN     = 'INVESTIGATOR_SAMPLE_ID'
MANIFEST__CMO_PATIENT_ID_COLUMN             = 'CMO_PATIENT_ID'
MANIFEST__SAMPLE_CLASS_COLUMN               = 'SAMPLE_CLASS'
MANIFEST__SAMPLE_TYPE_COLUMN                = 'SAMPLE_TYPE'
MANIFEST__LIBRARY_INPUT_COLUMN              = 'LIBRARY_INPUT[ng]'
MANIFEST__LIBRARY_YIELD_COLUMN              = 'LIBRARY_YIELD[ng]'
MANIFEST__CAPTURE_INPUT_COLUMN              = 'CAPTURE_INPUT[ng]'
MANIFEST__CAPTURE_BAIT_SET_COLUMN           = 'CAPTURE_BAIT_SET'
MANIFEST__SEX_COLUMN                        = 'SEX'
MANIFEST__LANE_COLUMN                       = 'LANE_NUMBER'
MANIFEST__PROJECT_ID_COLUMN                 = 'STUDY_ID'

manifest_columns = [
    MANIFEST__BARCODE_ID_COLUMN,
    MANIFEST__CAPTURE_NAME_COLUMN,
    MANIFEST__CMO_SAMPLE_ID_COLUMN,
    MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN,
    MANIFEST__CMO_PATIENT_ID_COLUMN,
    MANIFEST__SAMPLE_CLASS_COLUMN,
    MANIFEST__SAMPLE_TYPE_COLUMN,
    MANIFEST__LIBRARY_INPUT_COLUMN,
    MANIFEST__LIBRARY_YIELD_COLUMN,
    MANIFEST__CAPTURE_INPUT_COLUMN,
    MANIFEST__CAPTURE_BAIT_SET_COLUMN,
    MANIFEST__SEX_COLUMN,
    MANIFEST__BARCODE_INDEX_1_COLUMN,
    MANIFEST__BARCODE_INDEX_2_COLUMN,
    MANIFEST__LANE_COLUMN,
    MANIFEST__PROJECT_ID_COLUMN
]


##################################
# SampleSheet Column Definitions #
##################################

SAMPLE_SHEET__BARCODE_ID_COLUMN               = 'I5_Index_ID'
# Todo: Use a single barcode ID instead of I5 and I7
SAMPLE_SHEET__PROJECT_ID_COLUMN               = 'Sample_Project'
SAMPLE_SHEET__SAMPLE_ID_COLUMN                = 'Sample_ID'
SAMPLE_SHEET__COLLAB_ID_COLUMN                = 'Collab_ID'
SAMPLE_SHEET__PATIENT_ID_COLUMN               = 'Sample_Name'
SAMPLE_SHEET__CLASS_COLUMN                    = 'Description'
SAMPLE_SHEET__SAMPLE_TYPE_COLUMN              = 'Sample_type'
SAMPLE_SHEET__INPUT_NG_COLUMN                 = 'Input_ng'
SAMPLE_SHEET__LIBRARY_INPUT_COLUMN            = 'LIBRARY_INPUT[ng]'
SAMPLE_SHEET__LIBRARY_YIELD_COLUMN            = 'Library_yield'
SAMPLE_SHEET__POOL_INPUT_COLUMN               = 'Pool_input'
SAMPLE_SHEET__BAIT_VERSION_COLUMN             = 'Bait_version'
SAMPLE_SHEET__CAPTURE_INPUT_COLUMN            = 'CAPTURE_INPUT[ng]'
SAMPLE_SHEET__CAPTURE_BAIT_SET_COLUMN         = 'CAPTURE_BAIT_SET'
SAMPLE_SHEET__SEX_COLUMN                      = 'Sex'
SAMPLE_SHEET__BARCODE_INDEX_1_COLUMN          = 'index'
SAMPLE_SHEET__BARCODE_INDEX_2_COLUMN          = 'index2'
SAMPLE_SHEET__LANE_COLUMN                     = 'Lane'

# samplesheet_columns = [
#     SAMPLE_SHEET__BARCODE_ID_COLUMN,
#     SAMPLE_SHEET__PROJECT_ID_COLUMN,
#     SAMPLE_SHEET__SAMPLE_ID_COLUMN,
#     SAMPLE_SHEET__COLLAB_ID_COLUMN,
#     SAMPLE_SHEET__PATIENT_ID_COLUMN,
#     SAMPLE_SHEET__CLASS_COLUMN,
#     SAMPLE_SHEET__SAMPLE_TYPE_COLUMN,
#     SAMPLE_SHEET__INPUT_NG_COLUMN,
#     SAMPLE_SHEET__LIBRARY_INPUT_COLUMN,
#     SAMPLE_SHEET__LIBRARY_YIELD_COLUMN,
#     SAMPLE_SHEET__POOL_INPUT_COLUMN,
#     SAMPLE_SHEET__BAIT_VERSION_COLUMN,
#     SAMPLE_SHEET__CAPTURE_INPUT_COLUMN,
#     SAMPLE_SHEET__CAPTURE_BAIT_SET_COLUMN,
#     SAMPLE_SHEET__SEX_COLUMN,
#     SAMPLE_SHEET__BARCODE_INDEX_1_COLUMN,
#     SAMPLE_SHEET__BARCODE_INDEX_2_COLUMN,
#     SAMPLE_SHEET__LANE_COLUMN
# ]


################################
# TitleFile Column Definitions #
################################

TITLE_FILE__BARCODE_ID_COLUMN               = 'Barcode'
TITLE_FILE__POOL_COLUMN                     = 'Pool'
TITLE_FILE__SAMPLE_ID_COLUMN                = 'Sample'
TITLE_FILE__COLLAB_ID_COLUMN                = 'Collab_ID'
TITLE_FILE__PATIENT_ID_COLUMN               = 'Patient_ID'
TITLE_FILE__CLASS_COLUMN                    = 'Class'
TITLE_FILE__SAMPLE_TYPE_COLUMN              = 'Sample_type'
TITLE_FILE__INPUT_NG_COLUMN                 = 'Input_ng'
TITLE_FILE__LIBRARY_YIELD_COLUMN            = 'Library_yield'
TITLE_FILE__POOL_INPUT_COLUMN               = 'Pool_input'
TITLE_FILE__BAIT_VERSION_COLUMN             = 'Bait_version'
TITLE_FILE__SEX_COLUMN                      = 'Sex'
TITLE_FILE__BARCODE_INDEX_1_COLUMN          = 'Barcode_index_1'
TITLE_FILE__BARCODE_INDEX_2_COLUMN          = 'Barcode_index_2'
TITLE_FILE__LANE_COLUMN                     = 'Lane'


##########################
# Map Column Definitions #
##########################

# Use OrderedDict to keep ordering for keys() and values()
columns_map_manifest = OrderedDict([
    (MANIFEST__BARCODE_ID_COLUMN                 , TITLE_FILE__BARCODE_ID_COLUMN),
    (MANIFEST__CAPTURE_NAME_COLUMN               , TITLE_FILE__POOL_COLUMN),
    (MANIFEST__CMO_SAMPLE_ID_COLUMN              , TITLE_FILE__SAMPLE_ID_COLUMN),
    (MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN     , TITLE_FILE__COLLAB_ID_COLUMN),
    (MANIFEST__CMO_PATIENT_ID_COLUMN             , TITLE_FILE__PATIENT_ID_COLUMN),
    (MANIFEST__SAMPLE_CLASS_COLUMN               , TITLE_FILE__CLASS_COLUMN),
    (MANIFEST__SAMPLE_TYPE_COLUMN                , TITLE_FILE__SAMPLE_TYPE_COLUMN),
    (MANIFEST__LIBRARY_INPUT_COLUMN              , TITLE_FILE__INPUT_NG_COLUMN),
    (MANIFEST__LIBRARY_YIELD_COLUMN              , TITLE_FILE__LIBRARY_YIELD_COLUMN),
    (MANIFEST__CAPTURE_INPUT_COLUMN              , TITLE_FILE__POOL_INPUT_COLUMN),
    (MANIFEST__CAPTURE_BAIT_SET_COLUMN           , TITLE_FILE__BAIT_VERSION_COLUMN),
    (MANIFEST__SEX_COLUMN                        , TITLE_FILE__SEX_COLUMN),
    (MANIFEST__BARCODE_INDEX_1_COLUMN            , TITLE_FILE__BARCODE_INDEX_1_COLUMN),
    (MANIFEST__BARCODE_INDEX_2_COLUMN            , TITLE_FILE__BARCODE_INDEX_2_COLUMN),
    (MANIFEST__LANE_COLUMN                       , TITLE_FILE__LANE_COLUMN),
])

# Map SAMPLESHEET --> TITLE_FILE
# Use OrderedDict to keep ordering for keys() and values()
columns_map_samplesheet = OrderedDict([
    (SAMPLE_SHEET__BARCODE_ID_COLUMN             , TITLE_FILE__BARCODE_ID_COLUMN),
    (SAMPLE_SHEET__PROJECT_ID_COLUMN             , TITLE_FILE__POOL_COLUMN),
    (SAMPLE_SHEET__SAMPLE_ID_COLUMN              , TITLE_FILE__SAMPLE_ID_COLUMN),
    (SAMPLE_SHEET__COLLAB_ID_COLUMN              , TITLE_FILE__COLLAB_ID_COLUMN),
    (SAMPLE_SHEET__PATIENT_ID_COLUMN             , TITLE_FILE__PATIENT_ID_COLUMN),
    (SAMPLE_SHEET__CLASS_COLUMN                  , TITLE_FILE__CLASS_COLUMN),
    (SAMPLE_SHEET__SAMPLE_TYPE_COLUMN            , TITLE_FILE__SAMPLE_TYPE_COLUMN),
    (SAMPLE_SHEET__LIBRARY_INPUT_COLUMN          , TITLE_FILE__INPUT_NG_COLUMN),
    (SAMPLE_SHEET__LIBRARY_YIELD_COLUMN          , TITLE_FILE__LIBRARY_YIELD_COLUMN),
    (SAMPLE_SHEET__CAPTURE_INPUT_COLUMN          , TITLE_FILE__POOL_INPUT_COLUMN),
    (SAMPLE_SHEET__BAIT_VERSION_COLUMN           , TITLE_FILE__BAIT_VERSION_COLUMN),
    (SAMPLE_SHEET__SEX_COLUMN                    , TITLE_FILE__SEX_COLUMN),
    (SAMPLE_SHEET__BARCODE_INDEX_1_COLUMN        , TITLE_FILE__BARCODE_INDEX_1_COLUMN),
    (SAMPLE_SHEET__BARCODE_INDEX_2_COLUMN        , TITLE_FILE__BARCODE_INDEX_2_COLUMN),
    (SAMPLE_SHEET__LANE_COLUMN                   , TITLE_FILE__LANE_COLUMN),
])



##############################
# Pipeline Kickoff Constants #
##############################

NON_REVERSE_COMPLEMENTED = 0
REVERSE_COMPLEMENTED = 1

# Delimiter for printing logs
DELIMITER = '\n' + '*' * 20 + '\n'
# Delimiter for inputs file sections
INPUTS_FILE_DELIMITER = '\n\n' + '# ' + '--' * 30 + '\n\n'

# Template identifier string that will get replaced with the project root location
PIPELINE_ROOT_PLACEHOLDER = '$PIPELINE_ROOT'

BAM_REGEX = re.compile(r'.*\.bam$')

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
WALTZ_READ_COUNTS_FILENAME_SUFFIX = '.read-counts'
WALTZ_FRAGMENT_SIZES_FILENAME_SUFFIX = '.fragment-sizes'
WALTZ_INTERVALS_FILENAME_SUFFIX = '-intervals.txt'
WALTZ_INTERVALS_WITHOUT_DUPLICATES_FILENAME_SUFFIX = '-intervals-without-duplicates.txt'

TOTAL_OFF_TARGET_FRACTION_COLUMN = 'total_off_target_fraction'

WALTZ_CHROMOSOME_COLUMN = 'chromosome'
WALTZ_START_COLUMN = 'start'
WALTZ_STOP_COLUMN = 'stop'
WALTZ_INTERVAL_NAME_COLUMN = 'interval_name'
WALTZ_FRAGMENT_SIZE_COLUMN = 'fragment_size'
WALTZ_PEAK_COVERAGE_COLUMN = 'peak_coverage'
WALTZ_AVERAGE_COVERAGE_COLUMN = 'TotalCoverage'
WALTZ_GC_CONTENT_COLUMN = 'gc'

# todo
WALTZ_INTERVALS_FILE_HEADER = [
    WALTZ_CHROMOSOME_COLUMN,
    WALTZ_START_COLUMN,
    WALTZ_STOP_COLUMN,
    WALTZ_INTERVAL_NAME_COLUMN,
    WALTZ_FRAGMENT_SIZE_COLUMN,
    WALTZ_PEAK_COVERAGE_COLUMN,
    WALTZ_AVERAGE_COVERAGE_COLUMN,
    WALTZ_GC_CONTENT_COLUMN
]

WALTZ_COVERAGE_FILE_HEADER = ['TotalCoverage', 'UniqueCoverage']


# AGBM Metrics Files Constants
#
# Column names
AGBM_COVERAGE_FILENAME = 'waltz-coverage.txt'
AGBM_READ_COUNTS_FILENAME = 'read-counts.txt'
AGBM_FRAGMENT_SIZES_FILENAME = 'fragment-sizes.txt'
AGBM_INTERVALS_COVERAGE_SUM_FILENAME = 'intervals_coverage_sum.txt'


# fragment-sizes.txt
FRAGMENT_SIZE_COLUMN = 'FragmentSize'
TOTAL_FREQUENCY_COLUMN = 'TotalFrequency'
UNIQUE_FREQUENCY_COLUMN = 'UniqueFrequency'

# read-counts.txt
TOTAL_MAPPED_COLUMN = 'TotalMapped'
UNIQUE_MAPPED_COLUMN = 'UniqueMapped'
TOTAL_READS_COLUMN = 'TotalReads'
UNMAPPED_READS_COLUMN = 'UnmappedReads'
DUPLICATE_FRACTION_COLUMN = 'DuplicateFraction'
TOTAL_ON_TARGET_COLUMN = 'TotalOnTarget'
UNIQUE_ON_TARGET_COLUMN = 'UniqueOnTarget'
TOTAL_ON_TARGET_FRACTION_COLUMN = 'TotalOnTargetFraction'
UNIQUE_ON_TARGET_FRACTION_COLUMN = 'UniqueOnTargetFraction'

# File Headers
AGBM_READ_COUNTS_HEADER = [
    SAMPLE_ID_COLUMN,
    'bam',
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
    UNIQUE_FREQUENCY_COLUMN
]

# Chr\tStart\tEnd\tIntervalName\tLength\tGC\tCoverage\tCoverageWithoutDuplicates
# intervals-coverage-sum.txt
CHROMOSOME_COLUMN = 'Chr'
START_COLUMN = 'Start'
END_COLUMN = 'End'
INTERVAL_NAME_COLUMN = 'IntervalName'
LENGTH_COLUMN = 'Length'
GC_COLUMN = 'GC'
COVERAGE_COLUMN = 'Coverage'
COVERAGE_WITH_DUPLICATES_COLUMN = 'CoverageWithoutDuplicates'

AGBM_INTERVALS_COVERAGE_SUM_FILE_HEADER = [
    SAMPLE_ID_COLUMN,
    CHROMOSOME_COLUMN,
    START_COLUMN,
    END_COLUMN,
    INTERVAL_NAME_COLUMN,
    LENGTH_COLUMN,
    GC_COLUMN,
    COVERAGE_COLUMN,
    COVERAGE_WITH_DUPLICATES_COLUMN
]

AGBM_TOTAL_AVERAGE_COVERAGE_COLUMN = 'TotalCoverage'
AGBM_UNIQUE_AVERAGE_COVERAGE_COLUMN = 'UniqueCoverage'

AGBM_COVERAGE_HEADER = [
    SAMPLE_ID_COLUMN,
    AGBM_TOTAL_AVERAGE_COVERAGE_COLUMN,
    AGBM_UNIQUE_AVERAGE_COVERAGE_COLUMN
]


# TABLES MODULE Files Constants
#
# Labels for collapsing methods
TOTAL_LABEL = 'TotalCoverage'
PICARD_LABEL = 'Picard Unique'
MAPPED_LABEL = 'Mapped'

POOL_A_LABEL = 'A Targets'
POOL_B_LABEL = 'B Targets'

UNFILTERED_COLLAPSING_METHOD = 'All Unique'
SIMPLEX_COLLAPSING_METHOD = 'Simplex'
DUPLEX_COLLAPSING_METHOD = 'Duplex'

# Headers for tables
DUPLICATION_RATES_HEADER = [SAMPLE_ID_COLUMN, 'method', 'duplication_rate', 'pool']
GC_BIAS_HEADER = [SAMPLE_ID_COLUMN, 'interval_name', 'coverage', 'gc', 'method']
GC_BIAS_AVERAGE_COVERAGE_ALL_SAMPLES_HEADER = ['method', 'gc_bin', 'coverage']
GC_BIAS_AVERAGE_COVERAGE_EACH_SAMPLE_HEADER = ['method', SAMPLE_ID_COLUMN, 'gc_bin', 'coverage']

# Output file names
read_counts_filename = 'read-counts-agg.txt'
coverage_agg_filename = 'coverage-agg.txt'
each_sample_coverage_filename = 'GC-bias-with-coverage-averages-over-each-sample.txt'
gc_bias_with_coverage_filename = 'GC-bias-with-coverage.txt'
read_counts_total_filename = 'read-counts-total.txt'
coverage_per_interval_filename = 'coverage-per-interval.txt'

ALL_TABLES_MODULE_OUTPUT_FILES = [
    read_counts_filename,
    coverage_agg_filename,
    each_sample_coverage_filename,
    gc_bias_with_coverage_filename,
    read_counts_total_filename,
    coverage_per_interval_filename,
]


#########
# Noise #
#########

NOISE_HEADER = [SAMPLE_ID_COLUMN, 'GenotypeCount', 'AltCount', 'AltPercent', 'ContributingSites', 'Method']


########################
# Cleanup Outputs Step #
########################

TMPDIR_SEARCH = re.compile(r'^tmp......$')
OUT_TMPDIR_SEARCH = re.compile(r'^out_tmpdir......$')

STANDARD_BAM_DIR = 'standard_bams'
UNFILTERED_BAM_DIR = 'unfiltered_bams'
SIMPLEX_BAM_DIR = 'simplex_bams'
DUPLEX_BAM_DIR = 'duplex_bams'
TRIM_FILES_DIR = 'trimming_results'
MARK_DUPLICATES_FILES_DIR = 'mark_duplicates_results'
COVERED_INTERVALS_DIR = 'covered_intervals_results'

BAM_FILE_REGEX = re.compile(r'\.bam$')
STANDARD_BAM_SEARCH = re.compile(r'^.*_cl_aln_srt_MD_IR_FX_BR.bam$')
UNFILTERED_BAM_SEARCH = re.compile(r'^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX.bam$')
SIMPLEX_BAM_SEARCH = re.compile(r'^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-simplex.bam$')
DUPLEX_BAM_SEARCH = re.compile(r'^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-duplex.bam$')
STANDARD_BAI_SEARCH = re.compile(r'^.*_cl_aln_srt_MD_IR_FX_BR.bai$')
UNFILTERED_BAI_SEARCH = re.compile(r'^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX.bai$')
SIMPLEX_BAI_SEARCH = re.compile(r'^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-simplex.bai$')
DUPLEX_BAI_SEARCH = re.compile(r'^.*_cl_aln_srt_MD_IR_FX_BR__aln_srt_IR_FX-duplex.bai$')

TRIM_FILE_SEARCH = re.compile(r'^.*_cl\.stats$')
MARK_DUPLICATES_FILE_SEARCH = re.compile(r'^.*\.md_metrics$')
COVERED_INTERVALS_FILE_SEARCH = re.compile(r'^.*(\.fci\.bed\.srt|\.fci\.list)$')

BAM_DIRS = [
    STANDARD_BAM_DIR,
    UNFILTERED_BAM_DIR,
    SIMPLEX_BAM_DIR,
    DUPLEX_BAM_DIR
]

BAM_SEARCHES = [
    STANDARD_BAM_SEARCH,
    UNFILTERED_BAM_SEARCH,
    SIMPLEX_BAM_SEARCH,
    DUPLEX_BAM_SEARCH
]


#################
# HPC variables #
#################
# To-do define for LSF???
TOIL_BATCHSYSTEM = {
    "GRIDENGINE" : {
        "PE" : "smp",
        "ARGS_HOST" : {
            "phoenix-h1": "-q test.q",
            "phoenix-h2": "-q clin2.q"
        }
    },
    "LSF" : {
        "PE" : "",
        "ARGS_HOST" : {}
    }
}
