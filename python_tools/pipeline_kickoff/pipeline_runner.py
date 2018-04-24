import os
import argparse
import subprocess


###################################################################
# This script is used to run workflows from the command line.
# It does not submit jobs to worker nodes,
# as opposed to pipeline_submit,
# which uses bsub
#
# Optional, potentially useful Toil arguments:
#    --realTimeLogging \
#    --rotateLogging \
#    --js-console
# Todo: in 3.15 this argument no longer works. Might have been changed to --dontLinkImports
#    --linkImports \
#    --stats \
#    --debugWorker \
#
# Warning message to give to user:
#       2>&1 | awk '/Using the single machine batch system/ { system(
#       "printf \"\n\n \033[31m WARNING: You are running on the head node \n\n\ \033[m \" > /dev/stderr"
#       ) } { print $0 }'


BASE_TOIL_RUNNER = 'toil-cwl-runner'

DEFAULT_TOIL_ARGS = [
    '--preserve-environment PATH PYTHONPATH',
    '--defaultDisk 10G',
    '--defaultMem 10G',
    '--no-container',
    '--disableCaching',
    '--cleanWorkDir onSuccess',
    '--maxLogFileSize 20000000',
    '--logDebug',
]


def parse_arguments():
    parser = argparse.ArgumentParser(description='submit toil job')

    parser.add_argument(
        "--project_name",
        action="store",
        dest="project_name",
        help="Name for Project (e.g. pipeline_test)",
        required=True
    )

    parser.add_argument(
        "--output_location",
        action="store",
        dest="output_location",
        help="Path to CMO Project outputs location (e.g. /ifs/work/bergerm1/Innovation/sandbox/ian",
        required=True
    )

    parser.add_argument(
        "--inputs_file",
        action="store",
        dest="inputs_file",
        help="CWL Inputs file (e.g. inputs.yaml)",
        required=True
    )

    parser.add_argument(
        "--workflow",
        action="store",
        dest="workflow",
        help="Workflow .cwl Tool file (e.g. innovation_pipeline.cwl)",
        required=False
    )

    parser.add_argument(
        "--batch_system",
        action="store",
        dest="batch_system",
        help="(e.g. lsf or singleMachine)"
    )

    parser.add_argument(
        "--job_store_uuid",
        action="store",
        dest="job_store_uuid",
        help="(LSF & Toil job UUID)"
    )

    return parser.parse_args()


def create_directories(args):
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


def run_toil(args, output_directory, jobstore_path, logdir):

    cmd = ' '.join([BASE_TOIL_RUNNER] + DEFAULT_TOIL_ARGS + [
        '--outdir', output_directory,
        '--batchSystem', args.batch_system,
        '--writeLogs', logdir,
        '--logFile', logdir + '/cwltoil.log',
        '--workDir', output_directory,
        '--jobStore file://' + jobstore_path,
        args.workflow,
        args.inputs_file
    ])

    print "Running Toil with command: {}".format(cmd)
    subprocess.check_call(cmd, shell=True)


def main():
    args = parse_arguments()
    output_directory, jobstore_path, logdir = create_directories(args)
    run_toil(args, output_directory, jobstore_path, logdir)
