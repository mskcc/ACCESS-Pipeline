import argparse
import subprocess
import ruamel.yaml


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


DEFAULT_MEM = 5
DEFAULT_CPU = 1
DEFAULT_CONTROL_QUEUE = "sol"


def bsub(bsubline):
    '''
    Execute lsf bsub

    :param bsubline:
    :return:
    '''
    process = subprocess.Popen(bsubline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = process.stdout.readline()

    # fixme: need better exception handling
    print(output)
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
    job_command = ('{} ' * 6).format(
        'pipeline_runner',
        '--workflow ' + params.workflow,
        '--inputs_file ' + params.inputs_file,
        '--output_location ' + params.output_location,
        '--batch_system ' + params.batch_system,
        '--logLevel ' + params.log_level,
    )

    if params.restart:
        job_command += ' --restart '

    if params.service_class:
        job_command += ' --service_class {} '.format(params.service_class)

    # Grab the project name from the inputs file
    with open(params.inputs_file, 'r') as stream:
        inputs_yaml = ruamel.yaml.round_trip_load(stream)

    project_name = inputs_yaml['project_name']

    bsubline = [
        'bsub',
        '-cwd', '.',
        '-P', project_name,
        '-J', project_name,
        '-oo', project_name + "_stdout.log",
        '-eo', project_name + "_stderr.log",
        '-R', "rusage[mem={}]".format(DEFAULT_MEM),
        '-n', str(DEFAULT_CPU),
        '-q', params.leader_queue,
        '-Jd', project_name,
        '-W', params.max_walltime
    ]

    if params.leader_node:
        bsubline += ['-R', "select[hname={}]".format(params.leader_node)]

    bsubline += [job_command]

    lsf_job_id = bsub(bsubline)
    return project_name, lsf_job_id


def main():
    parser = argparse.ArgumentParser(description='Submit a pipeline leader job to the w01 node (specific for LUNA)')

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
        "--leader_node",
        action="store",
        dest="leader_node",
        help="Which node to use for leader job (e.g. w01 or ju01)"
    )

    parser.add_argument(
        "--leader_queue",
        action="store",
        dest="leader_queue",
        default=DEFAULT_CONTROL_QUEUE,
        help="Which queue to use for leader job (e.g. 'control')"
    )

    parser.add_argument(
        "--service_class",
        action="store",
        dest="service_class",
        help="Service class to use, if available (e.g. 'Berger')",
        required=False
    )

    parser.add_argument(
        "--restart",
        action="store_true",
        dest="restart",
        help="restart from an existing output directory",
        required=False
    )

    parser.add_argument(
        '--log_level',
        action='store',
        dest='log_level',
        default='INFO',
        help='INFO will just log the cwl filenames, DEBUG will include the actual commands being run (default is INFO)',
        required=False
    )

    parser.add_argument(
        '--max_walltime',
        action='store',
        dest='max_walltime',
        default=str(7*24*60),
        help='Run time limit before termination, in minutes (default: 7 days).',
        required=False
    )

    params = parser.parse_args()

    # Submit
    lsf_proj_name, lsf_job_id = submit_to_lsf(params)

    print(lsf_proj_name)
    print(lsf_job_id)



if __name__ == "__main__":
    main()
