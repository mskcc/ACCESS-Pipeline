import argparse
import subprocess


# This is a script to submit the leader toil-cwl-runner job to
# one of the worker nodes instead of the head node.
#
# This script is taken from Roslin's roslin_submit.py
#
# Todo: This script relies on bsub
# We would like it to work across batch systems.
# Use pipeline-runner.sh to use other batch systems,
# which runs the leader job on the head node.
#
# Todo: Include check for existing outputs directory


DEFAULT_MEM = 1
DEFAULT_CPU = 1
LEADER_NODE = "w01"
CONTROL_QUEUE = "control"


def bsub(bsubline):
    '''
    Execute lsf bsub

    :param bsubline:
    :return:
    '''
    process = subprocess.Popen(bsubline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = process.stdout.readline()

    # fixme: need better exception handling
    print output
    lsf_job_id = int(output.strip().split()[1].strip('<>'))

    return lsf_job_id


def submit_to_lsf(params):
    '''
    Submit pipeline_runner python script to the control node
    Todo: too many arguments, too many layers

    :param project_name:
    :param output_location:
    :param inputs_file:
    :param workflow:
    :param batch_system:
    :return:
    '''
    job_command = "{} {} {} {} {} {} {}".format(
        'pipeline_runner',
        '--project_name ' + params.project_name,
        '--workflow ' + params.workflow,
        '--inputs_file ' + params.inputs_file,
        '--output_location ' + params.output_location,
        '--batch_system ' + params.batch_system,
        '--logLevel ' + params.logLevel,
    )

    if params.restart:
        job_command += ' --restart '

    bsubline = [
        "bsub",
        "-cwd", '.',
        "-P", params.project_name,
        "-J", params.project_name,
        "-oo", params.project_name + "_stdout.log",
        "-eo", params.project_name + "_stderr.log",
        "-R", "select[hname={}]".format(LEADER_NODE),
        "-R", "rusage[mem={}]".format(DEFAULT_MEM),
        "-n", str(DEFAULT_CPU),
        "-q", CONTROL_QUEUE,
        "-Jd", params.project_name,
        job_command
    ]

    lsf_job_id = bsub(bsubline)
    return params.project_name, lsf_job_id


def main():
    parser = argparse.ArgumentParser(description='Submit a pipeline leader job to the w01 node (specific for LUNA)')

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
        help="Path to where outputs will be written",
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
        "--restart",
        action="store_true",
        dest="restart",
        help="restart from an existing output directory",
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

    params = parser.parse_args()

    # Submit
    lsf_proj_name, lsf_job_id = submit_to_lsf(params)

    print lsf_proj_name
    print lsf_job_id



if __name__ == "__main__":

    main()
