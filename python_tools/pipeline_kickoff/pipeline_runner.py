import os
import argparse
import subprocess


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
#    --stats \


# Command for Toil python executable
BASE_TOIL_RUNNER = 'toil-cwl-runner'

# Name for log file output by Toil
LOG_FILE_NAME = 'cwltoil.log'

# Defaults for our selection of Toil parameters
DEFAULT_TOIL_ARGS = {
    '--preserve-environment'    : 'PATH PYTHONPATH',
    '--defaultDisk'             : '10G',
    '--defaultMem'              : '10G',
    '--no-container'            : '',
    '--disableCaching'          : '',
    '--cleanWorkDir'            : 'onSuccess',
    '--logDebug'                : ''
    # '--maxLogFileSize':       : '20000000',
}


def parse_arguments():
    """
    Argparse wrapper

    :return:
    """
    parser = argparse.ArgumentParser(description='submit toil job')

    parser.add_argument(
        '--project_name',
        action='store',
        dest='project_name',
        help='Name for Project (e.g. pipeline_test)',
        required=True
    )

    parser.add_argument(
        '--output_location',
        action='store',
        dest='output_location',
        help='Path to CMO Project outputs location',
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
        help='(e.g. lsf or singleMachine)',
        required=True
    )

    parser.add_argument(
        '--job_store_uuid',
        action='store',
        dest='job_store_uuid',
        help='(LSF & Toil job UUID)',
        required=True
    )

    return parser.parse_known_args()


def create_directories(args):
    """
    Create a simple output directory structure for the the pipeline, which will include:

    - Pipeline outputs themselves
    - Log files
    - Temporary directories (deleted as per the cleanWorkDir parameter)
    - Jobstore directories (deleted as per cleanWorkDir parameter?)
    """
    project_name = args.project_name
    output_location = args.output_location
    job_store_uuid = args.job_store_uuid

    # Set output directory
    output_directory = "{}/{}".format(output_location, project_name)
    jobstore_base = "{}/tmp/".format(output_directory)
    jobstore_path = "{}/jobstore-{}".format(jobstore_base, job_store_uuid)
    logdir = os.path.join(output_directory, 'log')

    # Check if output directory already exists
    if os.path.exists(output_directory):
        print "The specified output directory already exists: {}".format(output_directory)

    print "Output Dir: " + output_directory
    print "Jobstore Base: " + jobstore_base

    # Create output directories
    os.makedirs(output_directory)
    os.makedirs(logdir)
    os.makedirs(jobstore_base)

    return output_directory, jobstore_path, logdir


def run_toil(args, output_directory, jobstore_path, logdir, unknowns):
    """
    Format and call the command to run CWL Toil
    """
    cmd = ' '.join(
        [BASE_TOIL_RUNNER] + [
        '--logFile', os.path.join(logdir, LOG_FILE_NAME),
        '--jobStore file://' + jobstore_path,
        '--batchSystem', args.batch_system,
        '--workDir', output_directory,
        '--outdir', output_directory,
        '--writeLogs', logdir,
        args.workflow,
        args.inputs_file
    ])

    ARG_TEMPLATE = ' {} {} '
    for arg, value in DEFAULT_TOIL_ARGS.items():
        if arg.replace('--', '') in unknowns:
            pass
        else:
            cmd += ARG_TEMPLATE.format(arg, value)

    # Override with user-supplied argument if found
    if len(unknowns) > 0:
        cmd += ' '.join(unknowns)

    print "Running Toil with command: {}".format(cmd)
    subprocess.check_call(cmd, shell=True)


########
# Main #
########

def main():
    args, unknowns = parse_arguments()

    output_directory, jobstore_path, logdir = create_directories(args)

    run_toil(args, output_directory, jobstore_path, logdir, unknowns)
