import os
import sys
import uuid
import argparse
import subprocess
import ruamel.yaml

from ..version import most_recent_tag


# This script is used to run workflows from the command line using toil-cwl-runner.
#
# It is a simple wrapper that creates the output directory structure,
# and provides some default values for Toil params.
#
# It does not submit jobs to worker nodes,
# as opposed to pipeline_submit, which uses bsub.
#
# Optional, potentially useful Toil arguments:
#    --realTimeLogging \
#    --rotateLogging \
#    --js-console
# Todo: in 3.15 this argument no longer works. Might have been changed to --dontLinkImports
#    --linkImports \
#    --clusterStats FILEPATH \
#    --stats \


# Command for Toil python executable
BASE_TOIL_RUNNER = 'toil-cwl-runner'

# Name for log file output by Toil
LOG_FILE_NAME = 'cwltoil.log'

# Environment variables needed to be preserved across nodes
PRESERVE_ENV_VARS = [
    'PATH',
    'PYTHONPATH',
    'LD_LIBRARY_PATH',
    'TOIL_LSF_ARGS',
    'TMPDIR',
    'TMP_DIR',
    'TEMP',
    'TMP',
    '_JAVA_OPTIONS',
]

# Defaults for our selection of Toil parameters
DEFAULT_TOIL_ARGS = {
    '--preserve-environment'    : ' '.join(PRESERVE_ENV_VARS),
    '--defaultDisk'             : '10G',
    '--defaultMem'              : '10G',
    '--no-container'            : '',
    '--disableCaching'          : '',
    '--stats'                   : '',
    '--cleanWorkDir'            : 'onSuccess',
    '--maxLogFileSize'          : '20000000000',
    '--retryCount'              : 2,
}


def parse_arguments():
    """
    Argparse wrapper

    Many of these arguments are simply passed through to the Toil runner
    :return:
    """
    parser = argparse.ArgumentParser(description='submit toil job')

    parser.add_argument(
        '--output_location',
        action='store',
        help='Path to CMO Project outputs location',
        required=True
    )

    parser.add_argument(
        '--inputs_file',
        action='store',
        help='CWL Inputs file (e.g. inputs.yaml)',
        required=True
    )

    parser.add_argument(
        '--workflow',
        action='store',
        help='Workflow .cwl Tool file (e.g. innovation_pipeline.cwl)',
        required=True
    )

    parser.add_argument(
        '--batch_system',
        action='store',
        help='e.g. lsf, sge or singleMachine',
        required=True
    )

    parser.add_argument(
        '--service_class',
        action='store',
        dest='service_class',
        help='e.g. Berger',
        required=False
    )

    parser.add_argument(
        '--restart',
        action='store_true',
        help='include this if we are restarting from an existing output directory',
        required=False
    )

    parser.add_argument(
        '--log_level',
        action='store',
        default='INFO',
        help='INFO will just log the cwl filenames, DEBUG will include the actual commands being run (default is INFO)',
        required=False
    )

    return parser.parse_known_args()


def get_project_name_and_pipeline_version_id(args):
    """
    Grab the project name and pipeline version from the run inputs file,
    and return as dash-separated string.

    :param args:
    :return:
    """
    with open(args.inputs_file, 'r') as stream:
        inputs_yaml = ruamel.yaml.round_trip_load(stream)

    project_name = inputs_yaml['project_name']
    pipeline_version = inputs_yaml['version']
    project_and_version_id = '-'.join([project_name, pipeline_version])

    return project_and_version_id


def create_directories(args):
    """
    Create a simple output directory structure for the the pipeline, which will include:

    - Pipeline outputs themselves
    - Log files
    - Temporary directories (deleted as per the cleanWorkDir parameter)
    - Jobstore directories (deleted as per cleanWorkDir parameter?)
    """
    output_location = args.output_location
    project_and_version_id = get_project_name_and_pipeline_version_id(args)

    # Export TOIL_LSF_PROJECT for this run
    # which will be passed to subsequent jobs with -P
    os.environ['TOIL_LSF_PROJECT'] = project_and_version_id

    # Set output directory
    output_directory = os.path.join(output_location, project_and_version_id)
    logdir = os.path.join(output_directory, 'log')
    tmpdir = '{}/tmp/'.format(output_directory)

    # Use existing jobstore, or create new one
    if args.restart:
        print('Looking for existing jobstore directory to restart run...')
        job_store_uuid = filter(lambda x: x.startswith('jobstore'), os.listdir(tmpdir))[0]
        jobstore_path = os.path.join(tmpdir, job_store_uuid)
    else:
        job_store_uuid = str(uuid.uuid1())
        jobstore_path = '{}/jobstore-{}'.format(tmpdir, job_store_uuid)

    # Check if output directory already exists
    if os.path.exists(output_directory) and not args.restart:
        raise Exception('The specified output directory already exists: {}'.format(output_directory))

    if not args.restart:
        # Create output directories
        os.makedirs(output_directory)
        os.makedirs(logdir)
        os.makedirs(tmpdir)

    print('Output Dir: ' + output_directory)
    print('Jobstore Base: ' + tmpdir)
    return output_directory, jobstore_path, logdir, tmpdir


def run_toil(args, output_directory, jobstore_path, logdir, tmpdir):
    """
    Format and call the command to run CWL Toil
    """
    cmd = ' '.join(
        [BASE_TOIL_RUNNER] + [
        '--logFile', os.path.join(logdir, LOG_FILE_NAME),
        '--jobStore', 'file://' + jobstore_path,
        '--batchSystem', args.batch_system,
        '--workDir', tmpdir,
        '--outdir', output_directory,
        '--writeLogs', logdir,
        '--logLevel', args.log_level,
    ])

    ARG_TEMPLATE = ' {} {} '

    # Include Default arguments
    for arg, value in DEFAULT_TOIL_ARGS.items():
        cmd += ARG_TEMPLATE.format(arg, value)

    # Include restart argument
    if args.restart:
        cmd += ' --restart '

    # End with the workflow and inputs.yaml file
    cmd += ARG_TEMPLATE.format(
        args.workflow,
        args.inputs_file
    )

    print('Running Toil with command: {}'.format(cmd))
    print('ACCESS-Pipeline version: {}'.format(most_recent_tag))
    sys.stdout.flush()
    subprocess.check_call(cmd, shell=True)


def set_temp_dir_env_vars(tmpdir):
    """
    Set environment variables for temporary directories
    Try to cover all possibilities for every tool

    :param tmpdir:
    :return:
    """
    os.environ['TMPDIR'] = tmpdir
    os.environ['TMP_DIR'] = tmpdir
    os.environ['TEMP'] = tmpdir
    os.environ['TMP'] = tmpdir
    os.environ['_JAVA_OPTIONS'] = '-Djava.io.tmpdir=' + tmpdir


########
# Main #
########

def main():
    args, unknowns = parse_arguments()

    if args.service_class:
        # Set SLA environment variable
        os.environ['TOIL_LSF_ARGS'] = ' -sla {} '.format(args.service_class)

    output_directory, jobstore_path, logdir, tmpdir = create_directories(args)

    set_temp_dir_env_vars(tmpdir)

    run_toil(args, output_directory, jobstore_path, logdir, tmpdir)
