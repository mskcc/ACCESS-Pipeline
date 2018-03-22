import os


# Define a constant for the root directory of this project
# Todo: there has to be a better way to reliably reference the project root
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(THIS_DIR, os.pardir))
ROOT_DIR = os.path.abspath(os.path.join(PARENT_DIR, os.pardir))

# Use root directory constant to reference further files:

#############
# Resources #
#############
RUN_PARAMS_PATH = os.path.join(ROOT_DIR, 'resources/run_params.yaml')
RUN_PARAMS_TEST_PATH = os.path.join(ROOT_DIR, 'resources/run_params__test.yaml')
FILE_RESOURCES_PATH = os.path.join(ROOT_DIR, 'resources/run_files.yaml')
