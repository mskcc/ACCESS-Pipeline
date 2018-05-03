import os
from collections import OrderedDict


# Define a constant for the root directory of this project
# Todo: Find better way to set project root while still using setup.py
ROOT_DIR = '/home/johnsoni/Innovation-Pipeline'


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
TEST_COLLAPSING                     = 'test__collapsing.yaml'
LOCAL_COLLAPSING                    = 'local__collapsing.yaml'
PRODUCTION_COLLAPSING               = 'production__collapsing.yaml'

# Run Files
RUN_FILES                           = os.path.join(RUN_FILES_FOLDER, PRODUCTION)
RUN_FILES_COLLAPSING                = os.path.join(RUN_FILES_FOLDER, PRODUCTION_COLLAPSING)
RUN_FILES_TEST                      = os.path.join(RUN_FILES_FOLDER, TEST)
RUN_FILES_TEST_COLLAPSING           = os.path.join(RUN_FILES_FOLDER, TEST_COLLAPSING)
RUN_FILES_LOCAL                     = os.path.join(RUN_FILES_FOLDER, LOCAL)
RUN_FILES_LOCAL_COLLAPSING          = os.path.join(RUN_FILES_FOLDER, LOCAL_COLLAPSING)

# Run Parameters
RUN_PARAMS                          = os.path.join(RUN_PARAMS_FOLDER, PRODUCTION)
RUN_PARAMS_COLLAPSING               = os.path.join(RUN_PARAMS_FOLDER, PRODUCTION_COLLAPSING)
RUN_PARAMS_TEST                     = os.path.join(RUN_PARAMS_FOLDER, TEST)
RUN_PARAMS_TEST_COLLAPSING          = os.path.join(RUN_PARAMS_FOLDER, TEST_COLLAPSING)

# Luna Resource Paths
TOOL_RESOURCES_LOCAL                = os.path.join(ROOT_DIR, 'resources/run_tools/local.yaml')
TOOL_RESOURCES_LUNA                 = os.path.join(ROOT_DIR, 'resources/run_tools/luna.yaml')

# Resource Overrides
RESOURCE_OVERRIDES_FILE_PATH        = os.path.join(ROOT_DIR, 'resources/resource_overrides.cwl')


############################################
# Manifest & Title File Column Definitions #
############################################

# Manifest Columns
MANIFEST__BARCODE_ID_COLUMN                 = 'BARCODE_ID'
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

# Use barcode index column as well,
# for adapter sequences.
# Todo use SampleSheet?
MANIFEST__BARCODE_INDEX_COLUMN              = 'BARCODE_INDEX'

# Title File columns
TITLE_FILE__BARCODE_ID_COLUMN               = 'Barcode'
TITLE_FILE__POOL_COLUMN                     = 'Pool'
TITLE_FILE__SAMPLE_ID_COLUMN                = 'Sample'
TITLE_FILE__COLLAB_ID_COLUMN                = 'Collab_ID'
TITLE_FILE__PATIENT_ID_COLUMN               = 'Patient_ID'
TITLE_FILE__CLASS_COLUMN                    = 'Class'
TITLE_FILE__SAMPLE_TYPE_COLUMN              = 'Sample_type'
TITLE_FILE__INPUT_NG_COLUMN                 = 'Input_ng'
TITLE_FILE__LIBRARAY_YIELD_COLUMN           = 'Library_yield'
TITLE_FILE__POOL_INPUT_COLUMN               = 'Pool_input'
TITLE_FILE__BAIT_VERSION_COLUMN             = 'Bait_version'
TITLE_FILE__GENDER_COLUMN                   = 'Gender'

TITLE_FILE__BARCODE_INDEX_COLUMN            = 'Barcode_index'

# Map MANIFEST --> TITLE_FILE
# Use OrderedDict to keep ordering for keys() and values()
columns_map = OrderedDict({
    MANIFEST__BARCODE_ID_COLUMN : TITLE_FILE__BARCODE_ID_COLUMN,
    MANIFEST__CAPTURE_NAME_COLUMN : TITLE_FILE__POOL_COLUMN,
    MANIFEST__CMO_SAMPLE_ID_COLUMN : TITLE_FILE__SAMPLE_ID_COLUMN,
    MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN : TITLE_FILE__COLLAB_ID_COLUMN,
    MANIFEST__CMO_PATIENT_ID_COLUMN : TITLE_FILE__PATIENT_ID_COLUMN,
    MANIFEST__SAMPLE_CLASS_COLUMN : TITLE_FILE__CLASS_COLUMN,
    MANIFEST__SAMPLE_TYPE_COLUMN : TITLE_FILE__SAMPLE_TYPE_COLUMN,
    MANIFEST__LIBRARY_INPUT_COLUMN : TITLE_FILE__INPUT_NG_COLUMN,
    MANIFEST__LIBRARY_YIELD_COLUMN : TITLE_FILE__LIBRARAY_YIELD_COLUMN,
    MANIFEST__CAPTURE_INPUT_COLUMN : TITLE_FILE__POOL_INPUT_COLUMN,
    MANIFEST__CAPTURE_BAIT_SET_COLUMN : TITLE_FILE__BAIT_VERSION_COLUMN,
    MANIFEST__SEX_COLUMN : TITLE_FILE__GENDER_COLUMN,
    MANIFEST__BARCODE_INDEX_COLUMN : TITLE_FILE__BARCODE_INDEX_COLUMN,
})

# Todo: ok to have 'Lane' colunn?
TITLE_FILE__LANE_COLUMN = 'Lane'


##########################
# Constants for QC files #
##########################

# Avoid division by zero errors
EPSILON = 1e-9

# WALTZ Metrics Files Constants

# Use same string for sample ID everywhere
SAMPLE_ID_COLUMN = TITLE_FILE__SAMPLE_ID_COLUMN

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
WALTZ_AVERAGE_COVERAGE_COLUMN = 'average_coverage'
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

WALTZ_COVERAGE_FILE_HEADER = ['total_coverage', 'unique_coverage']


# AGBM Metrics Files Constants
#
# Column names
AGBM_COVERAGE_FILENAME = 'waltz-coverage.txt'
AGBM_READ_COUNTS_FILENAME = 'read-counts.txt'
AGBM_FRAGMENT_SIZES_FILENAME = 'fragment-sizes.txt'
AGBM_INTERVALS_COVERAGE_SUM_FILENAME = 'intervals_coverage_sum.txt'

FRAGMENT_SIZE_COLUMN = 'fragment_size'
TOTAL_FREQUENCY_COLUMN = 'total_frequency'
UNIQUE_FREQUENCY_COLUMN = 'unique_frequency'

CHROMOSOME_COLUMN = 'chromosome'
START_COLUMN = 'start'
STOP_COLUMN = 'stop'
END_COLUMN = 'end'
INTERVAL_NAME_COLUMN = WALTZ_INTERVAL_NAME_COLUMN
LENGTH_COLUMN = 'length'
GC_COLUMN = 'gc'
COVERAGE_COLUMN = WALTZ_AVERAGE_COVERAGE_COLUMN
COVERAGE_WITH_DUPLICATES_COLUMN = 'coverage_with_duplicates'
COVERAGE_WITHOUT_DUPLICATES_COLUMN = 'coverage_without_duplicates'

TOTAL_MAPPED_COLUMN = 'total_mapped'
UNIQUE_MAPPED_COLUMN = 'unique_mapped'
TOTAL_READS_COLUMN = 'total_reads'
UNMAPPED_READS_COLUMN = 'unmapped_reads'
DUPLICATE_FRACTION_COLUMN = 'duplicate_fraction'
TOTAL_ON_TARGET_COLUMN = 'total_on_target'
UNIQUE_ON_TARGET_COLUMN = 'unique_on_target'
TOTAL_ON_TARGET_FRACTION_COLUMN = 'total_on_target_fraction'
UNIQUE_ON_TARGET_FRACTION_COLUMN = 'unique_on_target_fraction'

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

AGBM_INTERVALS_COVERAGE_SUM_FILE_HEADER = [
    SAMPLE_ID_COLUMN,
    CHROMOSOME_COLUMN,
    START_COLUMN,
    END_COLUMN,
    INTERVAL_NAME_COLUMN,
    LENGTH_COLUMN,
    GC_COLUMN,
    COVERAGE_COLUMN,
]

AGBM_TOTAL_AVERAGE_COVERAGE_COLUMN = WALTZ_AVERAGE_COVERAGE_COLUMN + '_total'
AGBM_UNIQUE_AVERAGE_COVERAGE_COLUMN = WALTZ_AVERAGE_COVERAGE_COLUMN + '_unique'

AGBM_COVERAGE_HEADER = [
    SAMPLE_ID_COLUMN,
    AGBM_TOTAL_AVERAGE_COVERAGE_COLUMN,
    AGBM_UNIQUE_AVERAGE_COVERAGE_COLUMN
]


# TABLES MODULE Files Constants
#
# Labels for collapsing methods
TOTAL_LABEL = 'total'
UNIQUE_LABEL = 'unique'
PICARD_LABEL = 'picard'
MAPPED_LABEL = 'mapped'
MARIANAS_UNFILTERED_COLLAPSING_METHOD = 'marianas_unfiltered'
MARIANAS_SIMPLEX_DUPLEX_COLLAPSING_METHOD = 'marianas_simplex_duplex'
MARIANAS_DUPLEX_COLLAPSING_METHOD = 'marianas_duplex'

# Headers for tables
DUPLICATION_RATES_HEADER = [SAMPLE_ID_COLUMN, 'method', 'duplication_rate']
INSERT_SIZE_PEAKS_HEADER = [SAMPLE_ID_COLUMN, 'peak_total', 'peak_total_size', 'peak_unique', 'peak_unique_size']
GC_BIAS_HEADER = [SAMPLE_ID_COLUMN, 'interval_name', 'coverage', 'gc', 'method']
GC_BIAS_AVERAGE_COVERAGE_ALL_SAMPLES_HEADER = ['method', 'gc_bin', 'coverage']
GC_BIAS_AVERAGE_COVERAGE_EACH_SAMPLE_HEADER = ['method', SAMPLE_ID_COLUMN, 'gc_bin', 'coverage']
