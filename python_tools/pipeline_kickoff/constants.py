import os
from collections import OrderedDict


# Define a constant for the root directory of this project
# Todo: Find better way to set project root while still using setup.py
ROOT_DIR = '/home/johnsoni/Innovation-Pipeline'


#############
# Resources #
#############

# Todo: Consolidate duplicate 'resources/local' string references:
# Local Resource Paths
LOCAL_TOOL_RESOURCES_FILE_PATH = os.path.join(ROOT_DIR, 'resources/local/tool_resources.yaml')
LOCAL_FILE_RESOURCES_PATH = os.path.join(ROOT_DIR, 'resources/local/run_files.yaml')
LOCAL_RUN_PARAMS_TEST_PATH = os.path.join(ROOT_DIR, 'resources/local/run_params__test.yaml')
LOCAL_RUN_PARAMS_COLLAPSING_PATH = os.path.join(ROOT_DIR, 'resources/local/run_params__collapsing.yaml')
RESOURCE_OVERRIDES_FILE_PATH = os.path.join(ROOT_DIR, 'resources/local/resource_overrides.cwl')

# Luna Resource Paths
RUN_PARAMS_PATH = os.path.join(ROOT_DIR, 'resources/production/run_params.yaml')
FILE_RESOURCES_PATH = os.path.join(ROOT_DIR, 'resources/production/run_files.yaml')
FILE_RESOURCES_TEST_PATH = os.path.join(ROOT_DIR, 'resources/test/run_files__test.yaml')
TOOL_RESOURCES_FILE_PATH = os.path.join(ROOT_DIR, 'resources/production/tool_resources.yaml')
RUN_PARAMS_TEST_PATH = os.path.join(ROOT_DIR, 'resources/test/run_params__test.yaml')
COLLAPSING_PARAMETERS_FILE_PATH = os.path.join(ROOT_DIR, 'resources/production/run_params__collapsing.yaml')
COLLAPSING_FILES_FILE_PATH = os.path.join(ROOT_DIR, 'resources/production/run_files__collapsing.yaml')


############################################
# Manifest & Title File Column Definitions #
############################################

# Manifest Columns
MANIFEST__BARCODE_ID_COLUMN = 'BARCODE_ID'
MANIFEST__CAPTURE_NAME_COLUMN = 'CAPTURE_NAME'
MANIFEST__CMO_SAMPLE_ID_COLUMN = 'CMO_SAMPLE_ID'
MANIFEST__INVESTIGATOR_SAMPLE_ID_COLUMN = 'INVESTIGATOR_SAMPLE_ID'
MANIFEST__CMO_PATIENT_ID_COLUMN = 'CMO_PATIENT_ID'
MANIFEST__SAMPLE_CLASS_COLUMN = 'SAMPLE_CLASS'
MANIFEST__SAMPLE_TYPE_COLUMN = 'SAMPLE_TYPE'
MANIFEST__LIBRARY_INPUT_COLUMN = 'LIBRARY_INPUT[ng]'
MANIFEST__LIBRARY_YIELD_COLUMN = 'LIBRARY_YIELD[ng]'
MANIFEST__CAPTURE_INPUT_COLUMN = 'CAPTURE_INPUT[ng]'
MANIFEST__CAPTURE_BAIT_SET_COLUMN = 'CAPTURE_BAIT_SET'
MANIFEST__SEX_COLUMN = 'SEX'

# Use barcode index column as well,
# for adapter sequences. Todo use SampleSheet
MANIFEST__BARCODE_INDEX_COLUMN = 'BARCODE_INDEX'

# Title File columns
TITLE_FILE__BARCODE_ID_COLUMN = 'Barcode'
TITLE_FILE__POOL_COLUMN = 'Pool'
TITLE_FILE__SAMPLE_ID_COLUMN = 'Sample_ID'
TITLE_FILE__COLLAB_ID_COLUMN = 'Collab_ID'
TITLE_FILE__PATIENT_ID_COLUMN = 'Patient_ID'
TITLE_FILE__CLASS_COLUMN = 'Class'
TITLE_FILE__SAMPLE_TYPE_COLUMN = 'Sample_type'
TITLE_FILE__INPUT_NG_COLUMN = 'Input_ng'
TITLE_FILE__LIBRARAY_YIELD_COLUMN = 'Library_yield'
TITLE_FILE__POOL_INPUT_COLUMN = 'Pool_input'
TITLE_FILE__BAIT_VERSION_COLUMN = 'Bait_version'
TITLE_FILE__GENDER_COLUMN = 'Gender'

# Use barcode index column as well,
# for adapter sequences. Todo use SampleSheet
TITLE_FILE__BARCODE_INDEX_COLUMN = 'Barcode_index'

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