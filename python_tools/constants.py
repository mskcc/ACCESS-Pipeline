import os
import re

from root import ROOT_DIR


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
TOOL_RESOURCES_LUNA                 = os.path.join(ROOT_DIR, 'resources/run_tools/luna.yaml')

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


##########################
# Constants for QC files #
##########################

# Avoid division by zero errors
EPSILON = 1e-9

# Shorter reference to sample ID column, to be used everywhere
SAMPLE_ID_COLUMN = MANIFEST__CMO_SAMPLE_ID_COLUMN

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
] + INSERT_SIZE_OUTPUT_FILE_NAMES + [
    'qc_sample_coverage_A_targets.txt',
    'qc_sample_coverage_B_targets.txt'
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
TMPDIR_SEARCH_2 = re.compile(r'^tmp$')

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
