import os
import sys
import uuid
import argparse
import subprocess
import ruamel.yaml

import version
from python_tools.constants import TOIL_BATCHSYSTEM


###################################################################
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

# Defaults for our selection of Toil parameters
DEFAULT_TOIL_ARGS = {
    '--preserve-environment'    : 'PATH PYTHONPATH TOIL_LSF_ARGS',
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
        dest='output_location',
        help='Path to Project outputs location',
        required=True
    )

    parser.add_argument(
        '--inputs_file',
        action='store',
        dest='inputs_file',
        help='CWL Inputs file (e.g. inputs.yaml)',
        required=True
    )

    parser.add_argument(
        '--workflow',
        action='store',
        dest='workflow',
        help='Workflow .cwl Tool file (e.g. innovation_pipeline.cwl)',
        required=True
    )

    parser.add_argument(
        '--batch_system',
        action='store',
        dest='batch_system',
        help='e.g. lsf, sge or singleMachine',
        required=True
    )

    parser.add_argument(
        '--batch_system_pe',
        action='store',
        dest='batch_system_pe',
        help='batch system parallel environment. e.g. smp for SGE',
        required=False
    )

    parser.add_argument(
        '--batch_system_args',
        action='store',
        dest='batch_system_args',
        help='batch system arguments',
        required=False
    )

    parser.add_argument(
        '--user_Rlibs',
        action='store_true',
        dest='user_Rlibs',
        help='set if environment variable R_LIBS is defined and to be used \
                in addition to the R site library',
        required=False
    )

    parser.add_argument(
        '--restart',
        action='store_true',
        dest='restart',
        help='include this if we are restarting from an existing output directory',
        required=False
    )

    parser.add_argument(
        '--logLevel',
        action='store',
        dest='logLevel',
        default='INFO',
        help='INFO will just log the cwl filenames, DEBUG will include the actual commands being run (default is INFO)',
        required=False
    )

    parser.add_argument(
        '--project_name',
        action='store',
        dest='project_name',
        default='INFO',
        help='Name for the processed data directory',
        required=False
    )

    parser.add_argument(
        '--include_version',
        action='store_false',
        dest='include_version',
        default='INFO',
        help='Include pipeline git version in the project directory name',
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
    
    if args.project_name:
        project_name = args.project_name
    else:
        project_name = inputs_yaml['project_name']
    if args.include_version:
        pipeline_version = inputs_yaml['version']
        project_name = '-'.join([project_name, pipeline_version])

    return project_name


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


def set_batch_system_env(args, TOIL_BATCHSYSTEM):
    """
    Set environmental variables for batch system
    """
    if args.batch_system == "gridEngine":
        BATCH_SYSTEM_PARAMETERS = TOIL_BATCHSYSTEM["GRIDENGINE"]
        if args.batch_system_pe:
            os.environ["TOIL_GRIDENGINE_PE"] = args.batch_system_pe
        else:
            os.environ["TOIL_GRIDENGINE_PE"] = BATCH_SYSTEM_PARAMETERS["PE"]

        if args.batch_system_args:
            os.environ["TOIL_GRIDENGINE_ARGS"] = args.batch_system_args
        elif BATCH_SYSTEM_PARAMETERS["ARGS_HOST"][os.environ["HOSTNAME"]]:
            os.environ["TOIL_GRIDENGINE_ARGS"] =\
                BATCH_SYSTEM_PARAMETERS["ARGS_HOST"][os.environ["HOSTNAME"]]
        else:
            pass
            # Use whatever deault queue avalable
    else:
        pass
        # To-Do set LSF variables
    return


def configure_miscellaneous(args):
    """
    configure minor settings and variables
    """
    if args.user_Rlibs is not True:
        os.environ['R_LIBS'] = ""
    return


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
        '--logLevel', args.logLevel,
    ])

    # Update environment variables if batch system is set
    #if args.batch_system:
    #    set_batch_system_env(args, TOIL_BATCHSYSTEM)
    
    # miscellaneous settings
    #configure_miscellaneous(args)

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
    print('ACCESS-Pipeline version: {}'.format(version.most_recent_tag))
    sys.stdout.flush()
    subprocess.check_call(cmd, shell=True)


########
# Main #
########

def main():
    args, unknowns = parse_arguments()

    output_directory, jobstore_path, logdir, tmpdir = create_directories(args)

    run_toil(args, output_directory, jobstore_path, logdir, tmpdir)
